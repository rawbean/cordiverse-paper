#!/usr/bin/env python3
"""Extract all catalog papers that do not yet have a reader."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from extract_paper import extract  # noqa: E402


def main() -> None:
    data = json.loads((ROOT / "site" / "papers.json").read_text(encoding="utf-8"))
    for p in data["papers"]:
        if p.get("path"):
            continue
        cat, pid = p["category"], p["id"]
        pdf = ROOT / p["file"]
        if not pdf.is_file():
            print(f"SKIP missing {pdf}")
            continue
        # file path is papers/<cat>/<id>/paper.pdf
        disk_cat = Path(p["file"]).parts[1]
        print(f"\n=== {pid} ({disk_cat}) ===")
        extract(disk_cat, pid)


if __name__ == "__main__":
    main()
