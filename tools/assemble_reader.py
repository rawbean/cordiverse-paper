#!/usr/bin/env python3
"""Assemble a Cordiverse-style four-column reader from extracted artifacts."""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from format_text import format_page_text  # noqa: E402

TEMPLATE = ROOT / "site" / "papers" / "featured" / "cordiverse" / "index.html"

FOOTER_SITE = """
<footer class="site">
  <p class="copy">© 2026 生睿·SURY</p>
  <p class="legal">本站由生睿软件（<a href="https://www.surysoft.com">www.surysoft.com</a>）提供，用于学术论文的对照阅读。中文译文、白话解读与读后评论仅供学习参考，不替代原文，亦不代表原作者立场。论文版权归原作者及权利人所有，引用请以原文为准。</p>
  <p class="suggest">如有推荐的论文或博客，请发送至 <a href="mailto:hi@sury.cn">hi@sury.cn</a></p>
</footer>
"""


def load_page_json(folder: Path, n: int, key: str) -> str:
    fp = folder / f"page-{n:03d}.json"
    if not fp.is_file():
        return ""
    data = json.loads(fp.read_text(encoding="utf-8"))
    return str(data.get(key) or "")


def extract_css(src: str) -> str:
    m = re.search(r"<style>(.*?)</style>", src, re.S)
    if not m:
        raise SystemExit("no <style> in cordiverse template")
    return m.group(1)


def extract_runtime_js(src: str) -> str:
    """JS after PAPER_DICT load: column toggles, paging, dictionary."""
    # last big <script> before </body>
    scripts = re.findall(r"<script>(?!  var _hmt)(.*?)</script>", src, re.S)
    # skip the tiny view-init script (first small one)
    candidates = [s for s in scripts if "STORAGE_KEY" in s]
    if not candidates:
        raise SystemExit("no runtime script with STORAGE_KEY")
    return candidates[-1]


def page_block(i: int, total: int, en: str, zh: str, plain: str) -> str:
    en_html = format_page_text(en)
    zh_html = format_page_text(zh) if zh.strip() else "<p>（待翻译）</p>"
    if plain.strip():
        plain_paras = "".join(f"<p>{html.escape(p.strip())}</p>" for p in re.split(r"\n{2,}", plain.strip()) if p.strip())
        if not plain_paras:
            plain_paras = f"<p>{html.escape(plain.strip())}</p>"
    else:
        plain_paras = "<p>（待白话）</p>"
    return f"""<section class="page-block" id="page-{i}" data-page="{i}">
  <div class="page-label">第 {i} / {total} 页</div>
  <div class="grid4">
    <div class="panel pdf" data-col="pdf"><img src="pages/page-{i:03d}.jpg" alt="PDF page {i}" loading="lazy" decoding="async"></div>
    <div class="panel ocr content" data-col="ocr" lang="en">{en_html}</div>
    <div class="panel zh content" data-col="zh" lang="zh-CN">{zh_html}</div>
    <div class="panel plain content" data-col="plain" lang="zh-CN"><div class="plain-tag">白话解读</div>{plain_paras}</div>
  </div>
</section>"""


def assemble(meta: dict) -> None:
    paper_id = meta["id"]
    # disk dir may differ from catalog category (cordiverse lives under featured/)
    disk_cat = meta["category"]
    site_cat = meta.get("site_category") or disk_cat
    art = ROOT / "papers" / disk_cat / paper_id / "artifacts"
    if not (art / "page_texts.json").is_file() and site_cat != disk_cat:
        art = ROOT / "papers" / site_cat / paper_id / "artifacts"
        disk_cat = site_cat
    category = disk_cat
    texts = json.loads((art / "page_texts.json").read_text(encoding="utf-8"))
    total = len(texts)
    zh_dir = art / "page_zh"
    plain_dir = art / "page_plain"
    guide = (art / "guide.html").read_text(encoding="utf-8")
    commentary = (art / "commentary.html").read_text(encoding="utf-8")

    tpl = TEMPLATE.read_text(encoding="utf-8")
    css = extract_css(tpl)
    runtime = extract_runtime_js(tpl)
    runtime = runtime.replace("cordis-paper-cols-v1", meta["storage_key"])
    runtime = re.sub(r"const total = \d+;", f"const total = {total};", runtime)

    pages = "\n".join(
        page_block(
            i,
            total,
            texts[i - 1],
            load_page_json(zh_dir, i, "zh"),
            load_page_json(plain_dir, i, "plain"),
        )
        for i in range(1, total + 1)
    )

    title = html.escape(meta["title_short"])
    authors = html.escape(meta.get("authors") or "")
    authors_html = (
        f'<p class="paper-authors" title="{authors}">{authors}</p>' if authors else ""
    )
    html_out = f"""<!DOCTYPE html>
<html lang="zh-CN" data-view="guide">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — 四栏对照</title>
<style>
{css}
</style>
<script>
(function () {{
  var h = location.hash.slice(1);
  var v = "guide";
  if (h === "commentary") v = "comment";
  else if (/^page-\\d+$/.test(h)) v = "paper";
  document.documentElement.dataset.view = v;
}})();
</script>
<script src="dict/paper-dict.js"></script>
</head>
<body>
<header class="bar">
  <div class="brand">
    <a class="home" href="../../../index.html">
      <img class="mark" src="../../../assets/SurySoft-mark.svg" width="28" height="28" alt="生睿软件">
      <span class="logo">论文对照阅读</span>
    </a>
    <div class="paper-meta">
      <p class="paper-title" title="{title}">{title}</p>
      {authors_html}
    </div>
  </div>
  <nav class="view-tabs" role="tablist" aria-label="阅读分区">
    <a id="tab-guide" href="#guide" role="tab" aria-selected="true" data-view="guide">导读</a>
    <a id="tab-paper" href="#page-1" role="tab" aria-selected="false" data-view="paper">正文</a>
    <a id="tab-comment" href="#commentary" role="tab" aria-selected="false" data-view="comment">评论</a>
  </nav>
</header>
<article class="guide" id="guide" data-page="0">
  <div class="guide-inner">
{guide}
  </div>
</article>
<div class="paper-toolbar" id="paper-toolbar">
  <div class="col-toggles" role="group" aria-label="列显示">
    <span class="tog-label">显示列</span>
    <label class="tog on"><input type="checkbox" data-col-toggle="pdf" checked> PDF</label>
    <label class="tog on"><input type="checkbox" data-col-toggle="ocr" checked> 文本抽取</label>
    <label class="tog on"><input type="checkbox" data-col-toggle="zh" checked> 中文译文</label>
    <label class="tog on"><input type="checkbox" data-col-toggle="plain" checked> 白话解读</label>
  </div>
  <div class="controls">
    <button type="button" id="prev">上一页</button>
    <select id="jump" aria-label="跳转页码"></select>
    <button type="button" id="next">下一页</button>
  </div>
</div>
<div class="labels" id="col-labels">
  <span data-col="pdf">原始 PDF</span>
  <span data-col="ocr">文本抽取 · 划词即译</span>
  <span data-col="zh">中文译文</span>
  <span data-col="plain">白话解读</span>
</div>
{pages}
<article class="guide commentary" id="commentary">
  <div class="guide-inner">
{commentary}
    <div class="cta">
      <button type="button" id="comment-to-guide">回导读</button>
      <button type="button" id="comment-to-paper">从第 1 页读起</button>
      <span class="hint">评论在正文之后；用顶栏「评论」可随时跳到这里。</span>
    </div>
  </div>
</article>
<footer class="note">
  顶栏三个标签切换导读、正文与评论。正文工具栏可开关列（至少一列）；可见列横向均分撑满。英文「文本抽取」列支持划词查词：离线词库。快捷键：←/→ 或 K/J。
</footer>
{FOOTER_SITE}
<div id="dict-pop" role="dialog" aria-live="polite"></div>
<script>
{runtime}
</script>
</body>
</html>
"""
    dest = ROOT / "site" / "papers" / category / paper_id / "index.html"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(html_out, encoding="utf-8")
    print(f"wrote {dest}  pages={total}  bytes={dest.stat().st_size}")


def catalog() -> list[dict]:
    data = json.loads((ROOT / "site" / "papers.json").read_text(encoding="utf-8"))
    return list(data.get("papers") or [])


def meta_from_catalog(paper_id: str) -> dict:
    for p in catalog():
        if p.get("id") == paper_id:
            title = p.get("titleZh") or p.get("title") or paper_id
            return {
                "category": p["category"] if p["category"] != "runtime" else (
                    "featured" if paper_id == "cordiverse" else p["category"]
                ),
                "id": paper_id,
                "title_short": title,
                "authors": p.get("authors") or "",
                "storage_key": f"{paper_id}-paper-cols-v1",
                "site_category": p["category"],
            }
    raise SystemExit(f"unknown paper id: {paper_id}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("id")
    args = ap.parse_args()
    assemble(meta_from_catalog(args.id))


if __name__ == "__main__":
    main()
