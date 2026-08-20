#!/usr/bin/env python3
"""Write sitemap.xml and inject SEO tags into paper reader pages."""
from __future__ import annotations

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
PAPERS = json.loads((SITE / "papers.json").read_text(encoding="utf-8"))
ORIGIN = ""
site_cfg = SITE / "site.json"
if site_cfg.exists():
    ORIGIN = str(json.loads(site_cfg.read_text(encoding="utf-8")).get("origin") or "").rstrip("/")

BEGIN = "<!-- seo -->"
END = "<!-- /seo -->"


def abs_url(path: str) -> str:
    path = "/" + path.lstrip("/")
    return f"{ORIGIN}{path}" if ORIGIN else path


def xml_esc(s: str) -> str:
    return (
        str(s)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def write_sitemap() -> None:
    urls = [
        ("/", "weekly", "1.0"),
        ("/updates.html", "weekly", "0.6"),
    ]
    for p in PAPERS.get("papers") or []:
        path = str(p.get("path") or "").strip()
        if not path:
            continue
        urls.append(("/" + path.lstrip("/"), "monthly", "0.8"))
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for loc, freq, pri in urls:
        lines.append("  <url>")
        lines.append(f"    <loc>{xml_esc(abs_url(loc))}</loc>")
        lines.append(f"    <changefreq>{freq}</changefreq>")
        lines.append(f"    <priority>{pri}</priority>")
        lines.append("  </url>")
    lines.append("</urlset>")
    (SITE / "sitemap.xml").write_text("\n".join(lines) + "\n", encoding="utf-8")


def paper_seo(p: dict) -> str:
    title_zh = p.get("titleZh") or p.get("title") or p.get("id")
    title_en = p.get("title") or title_zh
    authors = p.get("authors") or ""
    source = p.get("source") or ""
    path = "/" + str(p.get("path") or "").lstrip("/")
    desc = f"《{title_zh}》中英对照阅读"
    if title_en and title_en != title_zh:
        desc += f"（{title_en}）"
    if authors:
        desc += f"。作者：{authors}"
    desc += "。含白话导读与读后评论，由生睿软件提供。"
    page_title = f"{title_zh} — 论文对照阅读"
    icon = "../../../assets/SurySoft-mark.svg"
    ld = {
        "@context": "https://schema.org",
        "@type": "ScholarlyArticle",
        "headline": title_zh,
        "name": title_zh,
        "inLanguage": ["zh-CN", "en"],
        "isPartOf": {"@type": "WebSite", "name": "论文对照阅读"},
        "publisher": {
            "@type": "Organization",
            "name": "生睿软件",
            "url": "https://www.surysoft.com",
        },
    }
    if title_en and title_en != title_zh:
        ld["alternativeHeadline"] = title_en
    if authors:
        ld["author"] = {"@type": "Person", "name": authors}
    if source:
        ld["sameAs"] = source
    if ORIGIN:
        ld["url"] = abs_url(path)
    attrs = [
        f'<title>{html.escape(page_title)}</title>',
        f'<meta name="description" content="{html.escape(desc)}">',
        '<meta name="robots" content="index,follow">',
        f'<meta name="author" content="{html.escape(authors or "生睿软件")}">',
        f'<link rel="canonical" href="{html.escape(abs_url(path))}">',
        f'<link rel="icon" href="{icon}" type="image/svg+xml">',
        '<meta property="og:type" content="article">',
        '<meta property="og:locale" content="zh_CN">',
        '<meta property="og:site_name" content="论文对照阅读">',
        f'<meta property="og:title" content="{html.escape(title_zh)}">',
        f'<meta property="og:description" content="{html.escape(desc)}">',
        f'<meta property="og:url" content="{html.escape(abs_url(path))}">',
        '<meta name="twitter:card" content="summary">',
        f'<meta name="citation_title" content="{html.escape(title_en)}">',
    ]
    if authors:
        attrs.append(f'<meta name="citation_author" content="{html.escape(authors)}">')
    if source:
        attrs.append(f'<link rel="alternate" href="{html.escape(source)}" title="原文">')
    attrs.append(
        '<script type="application/ld+json">'
        + json.dumps(ld, ensure_ascii=False, separators=(",", ":"))
        + "</script>"
    )
    return BEGIN + "\n" + "\n".join(attrs) + "\n" + END


def inject_paper(path: Path, p: dict) -> None:
    text = path.read_text(encoding="utf-8")
    block = paper_seo(p)
    if BEGIN in text and END in text:
        text = re.sub(
            re.escape(BEGIN) + r".*?" + re.escape(END),
            block,
            text,
            count=1,
            flags=re.S,
        )
    else:
        text = re.sub(
            r"<title>.*?</title>\s*",
            block + "\n",
            text,
            count=1,
            flags=re.S,
        )
    path.write_text(text, encoding="utf-8")


def write_index_noscript() -> None:
    items = []
    for p in PAPERS.get("papers") or []:
        path = str(p.get("path") or "").strip()
        if not path:
            continue
        href = path.rstrip("/") + "/index.html"
        title = p.get("titleZh") or p.get("title") or p.get("id")
        items.append(f'<li><a href="{html.escape(href)}">{html.escape(title)}</a></li>')
    block = (
        "<!-- seo-noscript -->\n"
        f'<noscript><nav aria-label="馆藏目录"><ul>{"".join(items)}</ul></nav></noscript>\n'
        "<!-- /seo-noscript -->"
    )
    index = SITE / "index.html"
    text = index.read_text(encoding="utf-8")
    if "<!-- seo-noscript -->" not in text:
        raise SystemExit("index.html missing seo-noscript markers")
    text = re.sub(
        r"<!-- seo-noscript -->.*?<!-- /seo-noscript -->",
        block,
        text,
        count=1,
        flags=re.S,
    )
    index.write_text(text, encoding="utf-8")


def main() -> None:
    write_sitemap()
    write_index_noscript()
    n = 0
    for p in PAPERS.get("papers") or []:
        rel = str(p.get("path") or "").strip().strip("/")
        if not rel:
            continue
        html_path = SITE / rel / "index.html"
        if not html_path.is_file():
            raise SystemExit(f"missing {html_path}")
        inject_paper(html_path, p)
        n += 1
    print(f"sitemap + noscript + {n} paper pages")


if __name__ == "__main__":
    main()
