#!/usr/bin/env python3
"""Build dict, assemble reader, and register path for a catalog paper."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def set_path(paper_id: str, path: str) -> None:
    fp = ROOT / "site" / "papers.json"
    data = json.loads(fp.read_text(encoding="utf-8"))
    found = False
    for p in data["papers"]:
        if p.get("id") == paper_id:
            p["path"] = path if path.endswith("/") else path + "/"
            found = True
            break
    if not found:
        raise SystemExit(f"not in papers.json: {paper_id}")
    fp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"registered path {path} for {paper_id}")


def main() -> None:
    if len(sys.argv) < 3:
        raise SystemExit("usage: finish_paper.py <category> <id>")
    category, paper_id = sys.argv[1], sys.argv[2]
    subprocess.check_call([sys.executable, str(ROOT / "tools" / "build_paper_dict.py"), category, paper_id])
    subprocess.check_call([sys.executable, str(ROOT / "tools" / "assemble_reader.py"), paper_id])
    set_path(paper_id, f"papers/{category}/{paper_id}/")


if __name__ == "__main__":
    main()
