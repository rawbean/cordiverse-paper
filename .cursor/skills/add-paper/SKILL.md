---
name: add-paper
description: >-
  Adds a new bilingual four-column paper reader under
  site/papers/<category>/<id>/. Use when the user wants to add a paper,
  新增论文, ingest a PDF into the reading site, or clone the Cordiverse
  reader for another document.
---

# 新增对照阅读论文

把一篇 PDF 做成与 `site/papers/featured/cordiverse/` 同构的阅读页，并登记进馆藏。参考实现只读 Cordiverse，不要改它的正文，除非用户要求。

## 用户至少要提供

- PDF 路径（或已在仓库里的文件）
- 文档 id：小写字母/数字/连字符，如 `cordiverse`
- 分类 category：须是 `site/papers.json` 里已有的主题分类（`runtime`、`cited-harness`、`protocol-loop`、`self-evolve`、`multi-agent`）。不要用 `featured` 当主题：`featured` 只是馆藏「推荐阅读」栏，由带 `path` 的篇目自动列入。
- 中英文标题、作者（缺则从 PDF 首页抽）

未指定 id 时，从英文标题生成短 slug，先给用户确认再开工。未指定 category 时，先确认主题分类；不要为了「推荐」去改 category，登记 `path` 后会同时出现在推荐阅读与该主题栏。

对外 URL：`/papers/<category>/<id>/`。

## 目录约定

```
papers/<category>/<id>/paper.pdf     # 原始 PDF（先拷到这里再加工）
papers/<category>/<id>/artifacts/    # 仅该篇的中间产物
  page_texts.json
  page_zh/page-NNN.json
  page_plain/page-NNN.json
papers/_shared/dict/ecdict.csv       # 跨篇 ECDICT，可复用，勿重复下载
site/papers/<category>/<id>/         # 对外阅读页（仅对照阅读需要）
  index.html
  pages/page-NNN.jpg
  dict/paper-dict.js
site/papers.json
```

现有主题分类：`runtime`（运行时与可组合性）、`cited-harness`、`protocol-loop`、`self-evolve`、`multi-agent`。`featured` 是馆藏「推荐阅读」栏，不是目录分类。相关文献可只放 PDF 并登记 json，不必做四栏页。

用户给了任意 PDF 路径时：先复制为 `papers/<category>/<id>/paper.pdf`，后续只读这份。不要把新 PDF 扔在仓库根目录。

`site/papers.json` 条目：

```json
{
  "id": "<id>",
  "category": "<category>",
  "title": "<English title>",
  "titleZh": "<中文标题>",
  "authors": "<作者 / 单位>",
  "path": "papers/<category>/<id>/",
  "file": "papers/<category>/<id>/paper.pdf",
  "source": "https://github.com/<org>/<repo>",
  "curated": "2026-08"
}
```

`path` 相对 `site/`（对照阅读页，仅已组装的篇目需要）；`file` 相对仓库根（本地 PDF）；`source` 为原始出处 URL；`curated` 为整理年月 `YYYY-MM`。

馆藏卡片列表以 `papers.json` 为准，不要往顶栏加具体论文链接。

## 实现步骤

按顺序做，可并行翻译，不可跳过登记。

### 1. 抽页

用 PyMuPDF（`fitz`）：

- 文本：每页 `get_text("text")`，写入 `papers/<category>/<id>/artifacts/page_texts.json`（字符串数组，下标 0 = 第 1 页）
- 图：约 120 DPI（`Matrix(120/72, 120/72)`），JPEG 质量 70–75，保存 `site/papers/<category>/<id>/pages/page-NNN.jpg`
- 去掉页脚孤零页码；英文断词 `word-\nword` 拼回

### 2. 按页中文

对**每一页抽取文本**整页翻译（不要跨页拼段落再映射）。

- 学术书面语；术语全文一致
- 保留公式、引用号 `[n]`、代码标识符、专名
- `Definition/Theorem/Lemma/Proof` → `定义/定理/引理/证明`
- 参考文献页：书目可留英文，标题译「参考文献」
- 输出 `papers/<category>/<id>/artifacts/page_zh/page-NNN.json`：`{"page":N,"zh":"..."}`

### 3. 按页白话

面向非形式化读者，120–280 字（目录/文献页可更短）。讲「本页在讲什么、为何重要、一个类比」，少堆公式。

输出 `papers/<category>/<id>/artifacts/page_plain/page-NNN.json`：`{"page":N,"plain":"..."}`。

### 4. 离线划词词典

- 从该文英文抽取词表（小写、去标点）
- 用 ECDICT（若已有 `papers/_shared/dict/ecdict.csv` 则复用，不要重复下 63MB）筛子集
- 论文术语用 glossary 覆盖/前置
- 写出 `site/papers/<category>/<id>/dict/paper-dict.js`：`window.PAPER_DICT={dict:{word:{t,p?}},alias:{}}`

### 5. 组装 `index.html`

以 `site/papers/<category>/<id>/` 为根，资源用**相对路径**：`pages/page-001.jpg`、`dict/paper-dict.js`。

必须具备（对齐 Cordiverse）：

| 能力 | 要求 |
|------|------|
| 馆藏 | 顶栏品牌与馆藏首页一致：标志 +「论文对照阅读」链到 `../../../index.html`；顶栏展示该篇中文标题，其下为作者信息 |
| 导读 / 正文 / 评论 | 三个 Tab，真链接 `#guide` / `#page-k` / `#commentary`，不是纯按钮 |
| 四栏 | 仅正文 Tab：PDF 图 · 结构化英文 · 结构化中文 · 白话；正文工具栏可开关列，至少一列，`--cols` 均分撑满横向 |
| 页码 | 仅正文 1..N；`#page-k`。导读与评论不占页码。列开关与翻页在正文工具栏，不进顶栏 |
| 排版 | 用 `tools/format_text.py` 的 `format_page_text`：标题/列表/定义/目录行 |
| 划词 | 仅在英文「文本抽取」列；读 `PAPER_DICT`；无外网 API |
| 导读 | 独立 Tab：主张、地图、精读路径；浓缩「和本领域的关系」 |
| 评论 | 独立 Tab，标明「读后评论 · 非论文原文」 |
| 统计 | `</head>` 前必须原样放入百度统计；HM ID `868def992b6aa420677094b2f0cd5486` 勿改、勿省略 |

```html
<script>
  var _hmt = _hmt || [];
  (function() {
    var hm = document.createElement("script");
    hm.src = "https://hm.baidu.com/hm.js?868def992b6aa420677094b2f0cd5486";
    var s = document.getElementsByTagName("script")[0];
    s.parentNode.insertBefore(hm, s);
  })();
</script>
```

中间栏与右栏必须**按页对齐**（第 k 页 OCR ↔ 第 k 页译文）。

宽度：内容壳不要 `max-width` 居中窄栏；可见列 `minmax(0,1fr)`。

### 6. 自检

- [ ] `site/papers/<category>/<id>/index.html`、全页 jpg、`dict/paper-dict.js` 存在
- [ ] `index.html` 的 `</head>` 前含 `hm.js?868def992b6aa420677094b2f0cd5486`
- [ ] `papers/<category>/<id>/paper.pdf` 已就位；`papers.json` 含 `path`、`file` 与 `source`
- [ ] `papers.json` 的 `path` 以 `/` 结尾，且 `category` 与目录一致
- [ ] 馆藏「进入阅读」指向 `papers/<category>/<id>/index.html`（不要只写目录路径）
- [ ] 硬刷新后：馆藏 → 进入阅读 → 馆藏；三个 Tab 与正文翻页可用
- [ ] 未改 Helm/Dockerfile（静态 `site/` 已覆盖新目录）

## 不要做

- 不要把新论文摊到 `site/` 或仓库根目录，也不要再写成 `papers/<id>/`（须带分类）
- 不要调用在线翻译/词典 API 作为运行时依赖
- 不要把 `papers/**/artifacts/`、`papers/_shared/` 打进镜像
- 不要重写已有论文，除非用户点名

## 用户侧最短提示词

用户以后对新对话可直接粘贴：

```
按 add-paper skill 新增一篇对照阅读。
- PDF：<路径>
- category：cited-harness
- id：<slug>
- 标题中/英：<...>
- 作者：<...>
做完登记 papers.json，并自检馆藏进出与导读/评论链接。
```
