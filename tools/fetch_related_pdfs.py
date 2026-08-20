#!/usr/bin/env python3
"""Download related-reading PDFs into papers/<category>/<id>/paper.pdf."""

from __future__ import annotations

import json
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
CURATED = "2026-08"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"

CATEGORIES = [
    {"id": "featured", "titleZh": "对照阅读", "title": "Bilingual readers"},
    {"id": "cited-harness", "titleZh": "论文已引用：Harness 与工具", "title": "Cited: harness and tools"},
    {"id": "protocol-loop", "titleZh": "协议、循环与工程实践", "title": "Protocols, loops, and practice"},
    {"id": "self-evolve", "titleZh": "自演化工具架", "title": "Self-evolving harnesses"},
    {"id": "multi-agent", "titleZh": "多智能体与编排", "title": "Multi-agent orchestration"},
]

# file is filled after download. source is the canonical origin URL.
PAPERS = [
    {
        "id": "cordiverse",
        "category": "featured",
        "title": "A Programming Paradigm for Spatiotemporal Composability",
        "titleZh": "一种面向时空可组合性的编程范式",
        "authors": "石一凡, 张伟, 崔天一 / Peking University, DeepSeek-AI",
        "path": "papers/featured/cordiverse/",
        "file": "papers/featured/cordiverse/paper.pdf",
        "source": "https://github.com/cordiverse/paper",
        "skip_fetch": True,
    },
    {
        "id": "harness-engineering",
        "category": "cited-harness",
        "title": "Harness Engineering: Leveraging Codex in an Agent-First World",
        "titleZh": "Harness 工程：在智能体优先的世界里用好 Codex",
        "authors": "R. Lopopolo / OpenAI",
        "source": "https://openai.com/index/harness-engineering/",
        "fetch": {"kind": "chrome", "url": "https://openai.com/index/harness-engineering/"},
    },
    {
        "id": "harness-design-long-running",
        "category": "cited-harness",
        "title": "Harness Design for Long-Running Application Development",
        "titleZh": "面向长时应用开发的 Harness 设计",
        "authors": "Anthropic",
        "source": "https://www.anthropic.com/engineering/harness-design-long-running-apps",
        "fetch": {
            "kind": "chrome",
            "url": "https://www.anthropic.com/engineering/harness-design-long-running-apps",
        },
    },
    {
        "id": "llm-agent-survey",
        "category": "cited-harness",
        "title": "A Survey on Large Language Model Based Autonomous Agents",
        "titleZh": "基于大语言模型的自主智能体综述",
        "authors": "L. Wang et al.",
        "source": "https://arxiv.org/abs/2308.11432",
        "fetch": {"kind": "arxiv", "id": "2308.11432"},
    },
    {
        "id": "tool-learning",
        "category": "cited-harness",
        "title": "Tool Learning with Foundation Models",
        "titleZh": "基础模型的工具学习",
        "authors": "Y. Qin et al.",
        "source": "https://arxiv.org/abs/2304.08354",
        "fetch": {"kind": "arxiv", "id": "2304.08354"},
    },
    {
        "id": "memgpt",
        "category": "cited-harness",
        "title": "MemGPT: Towards LLMs as Operating Systems",
        "titleZh": "MemGPT：走向作为操作系统的大语言模型",
        "authors": "C. Packer, V. Fang, S. G. Patil, et al.",
        "source": "https://arxiv.org/abs/2310.08560",
        "fetch": {"kind": "arxiv", "id": "2310.08560"},
    },
    {
        "id": "multi-agent-survey",
        "category": "cited-harness",
        "title": "Large Language Model Based Multi-Agents: A Survey of Progress and Challenges",
        "titleZh": "基于大语言模型的多智能体：进展与挑战综述",
        "authors": "T. Guo et al.",
        "source": "https://arxiv.org/abs/2308.10252",
        "fetch": {"kind": "arxiv", "id": "2308.10252"},
    },
    {
        "id": "latm",
        "category": "cited-harness",
        "title": "Large Language Models as Tool Makers",
        "titleZh": "大语言模型作为工具制造者",
        "authors": "T. Cai, X. Wang, T. Ma, X. Chen, D. Zhou",
        "source": "https://arxiv.org/abs/2305.17126",
        "fetch": {"kind": "arxiv", "id": "2305.17126"},
    },
    {
        "id": "react",
        "category": "protocol-loop",
        "title": "ReAct: Synergizing Reasoning and Acting in Language Models",
        "titleZh": "ReAct：在语言模型中协同推理与行动",
        "authors": "S. Yao et al.",
        "source": "https://arxiv.org/abs/2210.03629",
        "fetch": {"kind": "arxiv", "id": "2210.03629"},
    },
    {
        "id": "toolformer",
        "category": "protocol-loop",
        "title": "Toolformer: Language Models Can Teach Themselves to Use Tools",
        "titleZh": "Toolformer：语言模型可自学使用工具",
        "authors": "T. Schick et al.",
        "source": "https://arxiv.org/abs/2302.04761",
        "fetch": {"kind": "arxiv", "id": "2302.04761"},
    },
    {
        "id": "voyager",
        "category": "protocol-loop",
        "title": "Voyager: An Open-Ended Embodied Agent with Large Language Models",
        "titleZh": "Voyager：基于大语言模型的开放式具身智能体",
        "authors": "G. Wang et al.",
        "source": "https://arxiv.org/abs/2305.16291",
        "fetch": {"kind": "arxiv", "id": "2305.16291"},
    },
    {
        "id": "building-effective-agents",
        "category": "protocol-loop",
        "title": "Building Effective Agents",
        "titleZh": "如何构建有效的智能体",
        "authors": "Anthropic",
        "source": "https://www.anthropic.com/engineering/building-effective-agents",
        "fetch": {
            "kind": "chrome",
            "url": "https://www.anthropic.com/engineering/building-effective-agents",
        },
    },
    {
        "id": "mcp",
        "category": "protocol-loop",
        "title": "Introducing the Model Context Protocol",
        "titleZh": "模型上下文协议（MCP）发布",
        "authors": "Anthropic",
        "source": "https://www.anthropic.com/news/model-context-protocol",
        "fetch": {
            "kind": "chrome",
            "url": "https://www.anthropic.com/news/model-context-protocol",
        },
    },
    {
        "id": "swe-agent",
        "category": "self-evolve",
        "title": "SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering",
        "titleZh": "SWE-agent：智能体–计算机接口支撑自动软件工程",
        "authors": "J. Yang et al.",
        "source": "https://arxiv.org/abs/2405.15793",
        "fetch": {"kind": "arxiv", "id": "2405.15793"},
    },
    {
        "id": "codeact",
        "category": "self-evolve",
        "title": "Executable Code Actions Elicit Better LLM Agents",
        "titleZh": "CodeAct：可执行代码行动催生更好的 LLM 智能体",
        "authors": "X. Wang et al.",
        "source": "https://arxiv.org/abs/2402.01030",
        "fetch": {"kind": "arxiv", "id": "2402.01030"},
    },
    {
        "id": "darwin-godel-machine",
        "category": "self-evolve",
        "title": "Darwin Gödel Machine: Open-Ended Evolution of Self-Improving Agents",
        "titleZh": "达尔文–哥德尔机：自改进智能体的开放式演化",
        "authors": "J. Zhang et al.",
        "source": "https://arxiv.org/abs/2505.22954",
        "fetch": {"kind": "arxiv", "id": "2505.22954"},
    },
    {
        "id": "live-swe-agent",
        "category": "self-evolve",
        "title": "Live-SWE-agent: Can Software Engineering Agents Self-Evolve on the Fly?",
        "titleZh": "Live-SWE-agent：软件工程智能体能否在运行中自演化？",
        "authors": "C. S. Xia et al.",
        "source": "https://arxiv.org/abs/2511.13646",
        "fetch": {"kind": "arxiv", "id": "2511.13646"},
    },
    {
        "id": "generative-agents",
        "category": "self-evolve",
        "title": "Generative Agents: Interactive Simulacra of Human Behavior",
        "titleZh": "生成式智能体：人类行为的交互式拟像",
        "authors": "J. S. Park et al.",
        "source": "https://arxiv.org/abs/2304.03442",
        "fetch": {"kind": "arxiv", "id": "2304.03442"},
    },
    {
        "id": "autogen",
        "category": "multi-agent",
        "title": "AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation",
        "titleZh": "AutoGen：用多智能体对话支撑下一代 LLM 应用",
        "authors": "Q. Wu et al.",
        "source": "https://arxiv.org/abs/2308.08155",
        "fetch": {"kind": "arxiv", "id": "2308.08155"},
    },
    {
        "id": "metagpt",
        "category": "multi-agent",
        "title": "MetaGPT: Meta Programming for A Multi-Agent Collaborative Framework",
        "titleZh": "MetaGPT：面向多智能体协作框架的元编程",
        "authors": "S. Hong et al.",
        "source": "https://arxiv.org/abs/2308.00352",
        "fetch": {"kind": "arxiv", "id": "2308.00352"},
    },
    {
        "id": "camel",
        "category": "multi-agent",
        "title": "CAMEL: Communicative Agents for \"Mind\" Exploration of Large Language Model Society",
        "titleZh": "CAMEL：用交际智能体探索大语言模型社会",
        "authors": "G. Li et al.",
        "source": "https://arxiv.org/abs/2303.17760",
        "fetch": {"kind": "arxiv", "id": "2303.17760"},
    },
]


def dest_for(paper: dict) -> Path:
    if paper.get("file"):
        return ROOT / paper["file"]
    return ROOT / "papers" / paper["category"] / paper["id"] / "paper.pdf"


def is_pdf(path: Path) -> bool:
    if not path.is_file() or path.stat().st_size < 1000:
        return False
    with path.open("rb") as fh:
        return fh.read(5) == b"%PDF-"


def download_url(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = resp.read()
    dest.write_bytes(data)
    if not is_pdf(dest):
        raise RuntimeError(f"not a PDF ({len(data)} bytes): {url}")


def chrome_pdf(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(".tmp.pdf")
    if tmp.exists():
        tmp.unlink()
    cmd = [
        CHROME,
        "--headless=new",
        "--disable-gpu",
        "--no-pdf-header-footer",
        "--disable-blink-features=AutomationControlled",
        f"--user-agent={UA}",
        "--virtual-time-budget=25000",
        "--run-all-compositor-stages-before-draw",
        f"--print-to-pdf={tmp}",
        url,
    ]
    subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=180)
    if not is_pdf(tmp):
        raise RuntimeError(f"Chrome did not write a PDF for {url}")
    tmp.replace(dest)


def fetch_one(paper: dict) -> Path:
    dest = dest_for(paper)
    if paper.get("skip_fetch"):
        if not dest.is_file():
            raise FileNotFoundError(dest)
        return dest
    if is_pdf(dest):
        print(f"skip existing {dest.relative_to(ROOT)}")
        return dest
    spec = paper["fetch"]
    print(f"fetch {paper['id']} -> {dest.relative_to(ROOT)}")
    if spec["kind"] == "arxiv":
        download_url(f"https://arxiv.org/pdf/{spec['id']}.pdf", dest)
    elif spec["kind"] == "chrome":
        chrome_pdf(spec["url"], dest)
    else:
        raise ValueError(spec)
    time.sleep(0.4)
    return dest


def catalog_entry(paper: dict) -> dict:
    dest = dest_for(paper)
    entry = {
        "id": paper["id"],
        "category": paper["category"],
        "title": paper["title"],
        "titleZh": paper["titleZh"],
        "authors": paper["authors"],
        "file": str(dest.relative_to(ROOT)),
        "source": paper["source"],
        "curated": CURATED,
    }
    if paper.get("path"):
        entry["path"] = paper["path"]
    return entry


def main() -> int:
    failed = []
    for paper in PAPERS:
        try:
            fetch_one(paper)
        except Exception as exc:  # noqa: BLE001
            failed.append((paper["id"], str(exc)))
            print(f"FAIL {paper['id']}: {exc}", file=sys.stderr)

    catalog = {
        "categories": CATEGORIES,
        "papers": [catalog_entry(p) for p in PAPERS],
    }
    out = ROOT / "site" / "papers.json"
    out.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {out.relative_to(ROOT)}")
    if failed:
        print("failed:", failed, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
