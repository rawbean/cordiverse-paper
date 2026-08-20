#!/usr/bin/env python3
"""Bump or set Chart.yaml + values.yaml image.tag. Prints the new version."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHART = ROOT / "deploy/helm/cordiverse-paper/Chart.yaml"
VALUES = ROOT / "deploy/helm/cordiverse-paper/values.yaml"


def current() -> str:
    m = re.search(r"(?m)^version:\s*(\S+)", CHART.read_text())
    if not m:
        raise SystemExit("Chart.yaml 里没有 version")
    return m.group(1)


def bump(cur: str, part: str) -> str:
    major, minor, patch = (int(x) for x in cur.split("."))
    if part == "major":
        return f"{major + 1}.0.0"
    if part == "minor":
        return f"{major}.{minor + 1}.0"
    if part == "patch":
        return f"{major}.{minor}.{patch + 1}"
    raise SystemExit(f"未知 BUMP={part}，用 patch / minor / major 或 VERSION=x.y.z")


def write(new: str) -> None:
    chart = CHART.read_text()
    chart = re.sub(r"(?m)^version:\s*\S+", f"version: {new}", chart, count=1)
    chart = re.sub(r'(?m)^appVersion:\s*\S+', f'appVersion: "{new}"', chart, count=1)
    CHART.write_text(chart)
    values = VALUES.read_text()
    values = re.sub(r'(?m)^(\s*tag:\s*)"\d+\.\d+\.\d+"', rf'\1"{new}"', values, count=1)
    VALUES.write_text(values)


def main() -> None:
    cur = current()
    arg = sys.argv[1] if len(sys.argv) > 1 else "patch"
    if re.fullmatch(r"\d+\.\d+\.\d+", arg):
        new = arg
    else:
        new = bump(cur, arg)
    if new == cur:
        raise SystemExit(f"版本必须变更，当前已是 {cur}")
    write(new)
    print(new)


if __name__ == "__main__":
    main()
