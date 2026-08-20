#!/usr/bin/env python3
"""Assemble bilingual HTML from units.json + translations/*.json"""
import json
import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
units = json.loads((ROOT / "units.json").read_text(encoding="utf-8"))

zh_map = {}
trans_dir = ROOT / "translations"
if trans_dir.exists():
    for fp in sorted(trans_dir.glob("*.json")):
        data = json.loads(fp.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            for k, v in data.items():
                zh_map[int(k)] = v
        elif isinstance(data, list):
            for item in data:
                zh_map[int(item["id"])] = item["zh"]

HEADING_RE = re.compile(
    r"^(Abstract|References|\d+(\.\d+)*\.\s+\S|"
    r"(Definition|Theorem|Lemma|Corollary|Proposition|Remark|Example)\s+\d+|"
    r"Proof\.)$"
)


def classify(text: str) -> str:
    t = text.strip()
    first = t.split("\n", 1)[0].strip()
    if t.startswith("A Programming Paradigm"):
        return "title"
    if first == "Abstract":
        return "h1"
    if first == "References":
        return "h1"
    if re.match(r"^\d+\.\s+\S", first) and not re.match(r"^\d+\.\d+", first):
        return "h1"
    if re.match(r"^\d+\.\d+\.\s+\S", first) and not re.match(r"^\d+\.\d+\.\d+", first):
        return "h2"
    if re.match(r"^\d+\.\d+\.\d+\.\s+\S", first):
        return "h3"
    if re.match(
        r"^(Definition|Theorem|Lemma|Corollary|Proposition|Remark|Example)\s+\d+",
        first,
    ):
        return "def"
    if first == "Proof." or first.startswith("Proof."):
        return "proof"
    if first.startswith("•"):
        return "li"
    # formula-ish: lots of symbols, short-ish
    if len(t) < 200 and re.search(r"[∀∃→←∘⋄≃⊧≔∂ΓΣ]", t):
        return "math"
    return "p"


def esc(s: str) -> str:
    return html.escape(s).replace("\n", "<br>\n")


rows = []
for u in units:
    kind = classify(u["en"])
    en = u["en"]
    zh = zh_map.get(u["id"], "")
    if not zh:
        zh = '<span class="pending">（待翻译）</span>'
    else:
        zh = esc(zh)
    en_html = esc(en)
    rows.append(
        f'<section class="pair kind-{kind}" id="u{u["id"]}" data-section="{html.escape(u["section"])}">\n'
        f'  <div class="col en" lang="en">{en_html}</div>\n'
        f'  <div class="col zh" lang="zh-CN">{zh}</div>\n'
        f"</section>"
    )

css = r"""
:root {
  --ink: #1a1a1a;
  --muted: #5c5c5c;
  --rule: #d8d4cc;
  --bg: #f7f5f0;
  --en-bg: #faf9f6;
  --zh-bg: #f3f1eb;
  --accent: #0b4f6c;
  --def: #f0ebe0;
}
* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  margin: 0;
  font-family: "Iowan Old Style", "Palatino Linotype", Palatino, "Songti SC", "Source Han Serif SC", serif;
  color: var(--ink);
  background: var(--bg);
  line-height: 1.65;
}
header.site {
  position: sticky; top: 0; z-index: 10;
  background: rgba(247,245,240,.92);
  backdrop-filter: blur(8px);
  border-bottom: 1px solid var(--rule);
  padding: .75rem 1.25rem;
  display: flex; gap: 1rem; align-items: baseline; flex-wrap: wrap;
  justify-content: space-between;
}
header.site h1 {
  font-size: 1rem; margin: 0; font-weight: 600; color: var(--accent);
}
header.site .meta { color: var(--muted); font-size: .85rem; }
.col-labels {
  max-width: 1100px; margin: .75rem auto 0; padding: 0 1rem;
  display: grid; grid-template-columns: 1fr 1fr; gap: 0;
  font-size: .75rem; letter-spacing: .04em; text-transform: uppercase;
  color: var(--muted); font-family: "IBM Plex Sans", "Helvetica Neue", "PingFang SC", sans-serif;
}
.col-labels span { padding: 0 1rem; }
nav.toc {
  max-width: 1100px; margin: .5rem auto 1rem; padding: 0 1rem;
  font-size: .9rem; line-height: 1.9;
}
nav.toc a { color: var(--accent); text-decoration: none; margin-right: .85rem; white-space: nowrap; }
nav.toc a:hover { text-decoration: underline; }
main {
  max-width: 1100px;
  margin: 0 auto 3rem;
  padding: 0 .75rem;
  border: 1px solid var(--rule);
  background: #fff;
  box-shadow: 0 1px 0 rgba(0,0,0,.03);
}
.pair {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0;
  border-bottom: 1px solid var(--rule);
}
.pair:last-child { border-bottom: none; }
.col { padding: .85rem 1rem; font-size: .95rem; overflow-wrap: anywhere; }
.col.en { background: var(--en-bg); border-right: 1px solid var(--rule); }
.col.zh { background: var(--zh-bg); }
.kind-title .col { font-size: 1.35rem; font-weight: 650; line-height: 1.35; padding: 1.5rem 1rem; }
.kind-h1 .col { font-size: 1.25rem; font-weight: 700; color: var(--accent); padding-top: 1.4rem; }
.kind-h2 .col { font-size: 1.1rem; font-weight: 650; }
.kind-h3 .col { font-size: 1.02rem; font-weight: 600; }
.kind-def .col, .kind-proof .col {
  background: var(--def);
  font-family: "IBM Plex Sans", "Helvetica Neue", "PingFang SC", sans-serif;
  font-size: .9rem;
}
.kind-math .col {
  font-family: "Latin Modern Math", "Cambria Math", "Times New Roman", serif;
  font-size: .88rem;
  white-space: pre-wrap;
}
.kind-li .col { padding-left: 1.4rem; }
.pending { color: #a67c00; font-style: italic; }
footer.note {
  max-width: 1100px; margin: 0 auto 2rem; padding: 0 1rem;
  color: var(--muted); font-size: .8rem;
}
@media (max-width: 800px) {
  .pair, .col-labels { grid-template-columns: 1fr; }
  .col.en { border-right: none; border-bottom: 1px dashed var(--rule); }
  .col-labels span:last-child { margin-top: .25rem; }
}
"""

html_doc = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>时空可组合性的编程范式 — 中英对照</title>
<style>{css}</style>
</head>
<body>
<header class="site">
  <h1>A Programming Paradigm for Spatiotemporal Composability</h1>
  <span class="meta">中英对照 · Cordis Paper</span>
</header>
<nav class="toc">
  <a href="#u1">摘要</a>
  <a href="#u4">1 引言</a>
  <a href="#sec2">2 预备知识</a>
  <a href="#sec3">3 可逆效应与反应式余效应</a>
  <a href="#sec4">4 动态组合演算</a>
  <a href="#sec5">5 实现与案例</a>
  <a href="#sec6">6 讨论</a>
  <a href="#sec7">7 相关工作</a>
  <a href="#sec8">8 结论</a>
  <a href="#secrefs">参考文献</a>
</nav>
<div class="col-labels"><span>English</span><span>中文</span></div>
<main>
{chr(10).join(rows)}
</main>
<footer class="note">由 paper.pdf 抽取并人工校对术语后生成的中英对照稿；公式与参考文献条目尽量保留原文记号与书目信息。</footer>
<script>
const map = {{'2':'sec2','3':'sec3','4':'sec4','5':'sec5','6':'sec6','7':'sec7','8':'sec8','refs':'secrefs'}};
const seen = new Set();
document.querySelectorAll('section.pair').forEach(el => {{
  const s = el.dataset.section;
  if (map[s] && !seen.has(s)) {{ seen.add(s); el.id = map[s]; }}
}});
</script>
</body>
</html>
"""

out = ROOT / "paper-zh.html"
out.write_text(html_doc, encoding="utf-8")
# keep alias
(ROOT / "paper-bilingual.html").write_text(html_doc, encoding="utf-8")
translated = sum(1 for u in units if u["id"] in zh_map)
print(f"Wrote {out} and paper-bilingual.html ({translated}/{len(units)} translated)")
