#!/usr/bin/env python3
"""Build an offline PAPER_DICT subset from ECDICT + optional glossary."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ECDICT = ROOT / "papers" / "_shared" / "dict" / "ecdict.csv"
WORD = re.compile(r"[A-Za-z][A-Za-z'-]{1,}")

# Paper-specific terms to prepend (override ECDICT).
GLOSSARY = {
    "latm": {
        "tool maker": {"t": "工具制造者（LATM 中负责生成可复用 Python 工具的模型）"},
        "tool user": {"t": "工具使用者（用已造工具解具体实例的轻量模型）"},
        "dispatcher": {"t": "调度器（判断请求用缓存工具还是触发造新工具）"},
        "functional cache": {"t": "功能缓存：缓存的是一类请求的可执行工具，而非自然语言回答"},
        "chain of thought": {"t": "思维链（CoT）"},
        "cot": {"t": "思维链（Chain of Thought）"},
    },
    "live-swe-agent": {
        "scaffold": {"t": "脚手架 / 智能体运行框架（工具、循环、提示的组合）"},
        "harness": {"t": "智能体运行框架（agent harness）"},
        "on-the-fly": {"t": "在运行中、当场（不必离线训练）"},
        "mini-swe-agent": {"t": "仅 bash 的极简软件工程智能体脚手架"},
        "swe-bench": {"t": "软件工程智能体基准：根据 GitHub issue 改仓库"},
        "self-evolve": {"t": "自演化：智能体在运行中改自己的工具或脚手架"},
    },
    "mcp": {"mcp": {"t": "模型上下文协议（Model Context Protocol）"}, "harness": {"t": "智能体运行框架"}},
    "memgpt": {"memgpt": {"t": "把上下文当虚拟内存管理的 LLM 操作系统式框架"}, "working context": {"t": "工作上下文（主上下文窗口）"}},
    "toolformer": {"toolformer": {"t": "能自学插入工具调用的语言模型"}, "self-supervised": {"t": "自监督"}},
    "react": {"react": {"t": "ReAct：协同推理与行动"}, "thought": {"t": "思考（推理轨迹中的一步）"}},
    "voyager": {"voyager": {"t": "开放式具身智能体"}, "skill library": {"t": "技能库"}},
    "autogen": {"autogen": {"t": "多智能体对话框架"}, "conversable": {"t": "可对话智能体"}},
    "metagpt": {"metagpt": {"t": "用标准作业程序组织的多智能体框架"}, "sop": {"t": "标准作业程序"}},
    "camel": {"camel": {"t": "角色扮演交际智能体框架"}, "inception prompting": {"t": "起始提示"}},
    "swe-agent": {"aci": {"t": "智能体–计算机接口（Agent-Computer Interface）"}, "swe-bench": {"t": "软件工程智能体基准"}},
    "codeact": {"codeact": {"t": "以可执行代码作为智能体行动的范式"}},
    "darwin-godel-machine": {"dgm": {"t": "达尔文–哥德尔机：开放式自改进智能体"}, "self-improve": {"t": "自改进"}},
    "generative-agents": {"generative agents": {"t": "生成式智能体"}, "memory stream": {"t": "记忆流"}},
    "tool-learning": {"tool learning": {"t": "工具学习"}},
    "harness-engineering": {"harness": {"t": "智能体运行框架（agent harness）"}},
    "harness-design-long-running": {"harness": {"t": "智能体运行框架（agent harness）"}},
    "building-effective-agents": {"workflow": {"t": "工作流"}, "agent": {"t": "智能体"}},
    "llm-agent-survey": {"autonomous agent": {"t": "自主智能体"}},
    "multi-agent-survey": {"multi-agent": {"t": "多智能体"}},
}


def words_from_texts(texts: list[str]) -> set[str]:
    out: set[str] = set()
    for t in texts:
        for w in WORD.findall(t.lower()):
            w = w.strip("-'")
            if len(w) >= 3:
                out.add(w)
    return out


def load_ecdict(needed: set[str]) -> dict:
    found = {}
    if not ECDICT.is_file():
        print(f"warn: missing {ECDICT}", file=sys.stderr)
        return found
    with ECDICT.open(encoding="utf-8", errors="replace", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            w = (row.get("word") or "").strip().lower()
            if w not in needed:
                continue
            t = (row.get("translation") or row.get("definition") or "").strip()
            if not t:
                continue
            entry = {"t": t}
            p = (row.get("phonetic") or "").strip()
            if p:
                entry["p"] = p
            found[w] = entry
            if len(found) >= len(needed):
                break
    return found


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("category")
    ap.add_argument("id")
    args = ap.parse_args()
    art = ROOT / "papers" / args.category / args.id / "artifacts"
    texts = json.loads((art / "page_texts.json").read_text(encoding="utf-8"))
    needed = words_from_texts(texts)
    dict_ = load_ecdict(needed)
    gloss = GLOSSARY.get(args.id, {})
    # glossary keys may be phrases; also inject as alias-free dict entries
    for k, v in gloss.items():
        dict_[k] = v
        if " " not in k:
            dict_[k] = v
    dest_dir = ROOT / "site" / "papers" / args.category / args.id / "dict"
    dest_dir.mkdir(parents=True, exist_ok=True)
    payload = {"dict": dict_, "alias": {}}
    js = "window.PAPER_DICT=" + json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    (dest_dir / "paper-dict.js").write_text(js, encoding="utf-8")
    print(f"wrote {dest_dir / 'paper-dict.js'}  words={len(dict_)}  from_text={len(needed)}")


if __name__ == "__main__":
    main()
