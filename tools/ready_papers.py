#!/usr/bin/env python3
"""List catalog papers whose zh/plain/guide/commentary are complete."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def disk_cat(p: dict) -> str:
    return Path(p["file"]).parts[1]


def status(p: dict) -> dict:
    cat, pid = disk_cat(p), p["id"]
    art = ROOT / "papers" / cat / pid / "artifacts"
    texts_fp = art / "page_texts.json"
    if not texts_fp.is_file():
        return {"id": pid, "ready": False, "reason": "no page_texts"}
    n = len(json.loads(texts_fp.read_text(encoding="utf-8")))
    zh = len(list((art / "page_zh").glob("page-*.json"))) if (art / "page_zh").is_dir() else 0
    plain = len(list((art / "page_plain").glob("page-*.json"))) if (art / "page_plain").is_dir() else 0
    guide = (art / "guide.html").is_file()
    comm = (art / "commentary.html").is_file()
    ready = zh >= n and plain >= n and guide and comm
    return {"id": pid, "cat": cat, "n": n, "zh": zh, "plain": plain, "guide": guide, "comm": comm, "ready": ready, "has_path": bool(p.get("path"))}


def main() -> None:
    data = json.loads((ROOT / "site" / "papers.json").read_text(encoding="utf-8"))
    rows = [status(p) for p in data["papers"] if not p.get("path") or True]
    for r in rows:
        if r.get("reason"):
            print(f"{r['id']:28} {r['reason']}")
            continue
        flag = "READY" if r["ready"] and not r["has_path"] else ("done" if r["has_path"] else "wait")
        print(f"{r['id']:28} {flag:5}  {r['zh']:3}/{r['n']:<3} zh  {r['plain']:3}/{r['n']:<3} plain  g={int(r['guide'])} c={int(r['comm'])}")


if __name__ == "__main__":
    main()
