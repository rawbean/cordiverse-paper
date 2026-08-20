#!/usr/bin/env python3
"""Extract page texts and JPEG rasters for a paper under papers/<category>/<id>/."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parents[1]
HYPHEN = re.compile(r"([A-Za-z])-\n([A-Za-z])")
LONE_PAGE = re.compile(r"^\s*\d{1,3}\s*$", re.M)


def clean_text(raw: str) -> str:
    text = HYPHEN.sub(r"\1\2", raw)
    lines = []
    for line in text.split("\n"):
        if LONE_PAGE.fullmatch(line):
            continue
        lines.append(line.rstrip())
    return "\n".join(lines).strip() + "\n"


def extract(category: str, paper_id: str) -> None:
    pdf = ROOT / "papers" / category / paper_id / "paper.pdf"
    if not pdf.is_file():
        raise SystemExit(f"missing {pdf}")
    art = ROOT / "papers" / category / paper_id / "artifacts"
    art.mkdir(parents=True, exist_ok=True)
    pages_dir = ROOT / "site" / "papers" / category / paper_id / "pages"
    pages_dir.mkdir(parents=True, exist_ok=True)

    doc = fitz.open(pdf)
    matrix = fitz.Matrix(120 / 72, 120 / 72)
    texts = []
    for i, page in enumerate(doc, start=1):
        texts.append(clean_text(page.get_text("text")))
        pix = page.get_pixmap(matrix=matrix, alpha=False)
        dest = pages_dir / f"page-{i:03d}.jpg"
        pix.save(str(dest), jpg_quality=72)
        print(f"  page {i}/{doc.page_count}  {dest.name}  {dest.stat().st_size}")

    (art / "page_texts.json").write_text(
        json.dumps(texts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"wrote {art / 'page_texts.json'}  ({len(texts)} pages)")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("category")
    p.add_argument("id")
    args = p.parse_args()
    extract(args.category, args.id)


if __name__ == "__main__":
    main()
