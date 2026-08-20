"""Convert extracted paper page text into structured HTML."""
from __future__ import annotations

import html
import re
from typing import Iterable

SOFT_HYPHEN = "\u00ad"
BULLET_CHARS = "•●◦▪▸·"

SECTION_HEAD = re.compile(r"^\d+(?:\.\d+)*\.\s+\S")
DEF_HEAD = re.compile(
    r"^(?:Definition|Theorem|Lemma|Corollary|Proposition|Remark|Example|"
    r"定义|定理|引理|推论|命题|注记|备注|例子|示例)\s*\d+"
)
NAMED_HEAD = re.compile(
    r"^(?:Abstract|Contents|References|Appendix|Acknowledgements|"
    r"摘要|目录|参考文献|附录|致谢)\s*$"
)
PROOF_HEAD = re.compile(r"^(?:Proof\.?|证明[。．.]?)\s*$")
BULLET_HEAD = re.compile(rf"^[{re.escape(BULLET_CHARS)}]\s*")
TOC_LINE = re.compile(r"(?:\.{3,}|(?:\s\.){4,})")
PAGE_NUM = re.compile(r"^\d{1,3}$")
SENTENCE_END = re.compile(r"[.!?。！？:：;；…]$")


def _is_structural(s: str) -> bool:
    return bool(
        NAMED_HEAD.match(s)
        or SECTION_HEAD.match(s)
        or DEF_HEAD.match(s)
        or PROOF_HEAD.match(s)
        or BULLET_HEAD.match(s)
        or TOC_LINE.search(s)
    )


def _is_section_title_only(s: str) -> bool:
    """True for heading lines that should not absorb following prose."""
    if NAMED_HEAD.match(s) or PROOF_HEAD.match(s):
        return True
    if SECTION_HEAD.match(s) and len(s) <= 120:
        body = re.sub(r"^\d+(?:\.\d+)*\.\s*", "", s)
        # title-only: no further sentence punctuation in the title body
        if body and not re.search(r"[.!?。！？:：]", body):
            return True
    if DEF_HEAD.match(s) and len(s) < 48:
        return True
    return False


def _cjk_ratio(text: str) -> float:
    if not text:
        return 0.0
    cjk = sum(1 for ch in text if "\u4e00" <= ch <= "\u9fff")
    return cjk / max(1, len(re.sub(r"\s", "", text)))


def _clean_lines(text: str) -> list[str]:
    text = text.replace(SOFT_HYPHEN, "").replace("\r\n", "\n").replace("\r", "\n")
    text = text.replace("\u2060", "")  # word joiner often before TOC page numbers
    out = []
    for line in text.split("\n"):
        s = line.rstrip()
        if not s.strip():
            out.append("")
            continue
        if PAGE_NUM.fullmatch(s.strip()):
            continue
        out.append(s.strip())
    return out


def join_blocks(text: str) -> list[str]:
    lines = _clean_lines(text)
    non_empty = [l for l in lines if l]
    mostly_cjk = _cjk_ratio("\n".join(non_empty)) > 0.25

    blocks: list[str] = []
    buf = ""

    def flush() -> None:
        nonlocal buf
        if buf.strip():
            blocks.append(re.sub(r"[ \t]+", " ", buf.strip()))
        buf = ""

    for s in lines:
        if not s:
            flush()
            continue

        # De-hyphenate English wraps: "...composabil-" + "ity ..."
        if buf and re.search(r"[A-Za-z][-‐-]$", buf):
            buf = re.sub(r"[-‐-]$", "", buf) + s
            continue

        if not buf:
            buf = s
            if _is_section_title_only(s) or TOC_LINE.search(s) or NAMED_HEAD.match(s) or PROOF_HEAD.match(s):
                flush()
            elif mostly_cjk and (BULLET_HEAD.match(s) or SENTENCE_END.search(s) or DEF_HEAD.match(s)):
                # Chinese pages are already paragraph-broken; keep line as block
                flush()
            continue

        # New structural unit → flush previous
        if _is_structural(s) or TOC_LINE.search(s):
            flush()
            buf = s
            if _is_section_title_only(s) or TOC_LINE.search(s) or BULLET_HEAD.match(s) and mostly_cjk:
                flush()
            elif mostly_cjk and SENTENCE_END.search(s):
                flush()
            continue

        # After a completed Chinese/English sentence block, next line is new paragraph
        if mostly_cjk:
            flush()
            buf = s
            if SENTENCE_END.search(s) or _is_section_title_only(s) or BULLET_HEAD.match(s):
                flush()
            continue

        # English soft wrap join
        if _is_section_title_only(buf):
            flush()
            buf = s
            continue

        buf = buf + " " + s

    flush()
    return blocks


def classify(block: str) -> tuple[str, str]:
    s = block.strip()
    if not s:
        return "empty", s
    if TOC_LINE.search(s):
        return "toc", s
    if NAMED_HEAD.match(s):
        return "h1", s
    if SECTION_HEAD.match(s) and _is_section_title_only(s):
        if re.match(r"^\d+\.\d+\.\d+\.\s+", s):
            return "h3", s
        if re.match(r"^\d+\.\d+\.\s+", s):
            return "h2", s
        return "h1", s
    if DEF_HEAD.match(s):
        return "def", s
    if PROOF_HEAD.match(s):
        return "proof-label", s
    if BULLET_HEAD.match(s) or re.match(r"^[-–—]\s+\S", s):
        body = BULLET_HEAD.sub("", s)
        body = re.sub(r"^[-–—]\s*", "", body)
        return "li", body
    # lead-in emphasis (short label + prose), e.g. "Temporal limitation. ..." / "时间局限。..."
    if re.match(r"^[A-Z][A-Za-z\- /]{1,36}\.\s+\S", s):
        label = s.split(".", 1)[0]
        if len(label) <= 28:
            return "p-lead", s
    if re.match(r"^[\u4e00-\u9fff]{2,8}[。．.]\s*\S", s):
        return "p-lead", s
    if len(s) < 240 and re.search(r"[∀∃→←∘⋄≃⊧≔∂ΓΣ∫⟦⟧]", s) and _cjk_ratio(s) < 0.15:
        return "math", s
    if len(s) < 110 and re.match(
        r"^(?:Yifan|Wei |Tianyi|石|张|崔|\d|Peking|DeepSeek|北京大学|作者)",
        s,
    ):
        return "meta", s
    return "p", s


def _render_lead(s: str) -> str:
    if "。" in s[:24]:
        a, b = s.split("。", 1)
        return (
            f'<p class="lead"><strong>{html.escape(a)}。</strong>'
            f"{html.escape(b)}</p>"
        )
    if ". " in s[:55]:
        a, b = s.split(". ", 1)
        return (
            f'<p class="lead"><strong>{html.escape(a)}.</strong> '
            f"{html.escape(b)}</p>"
        )
    return f"<p>{html.escape(s)}</p>"


def _render_toc(s: str) -> str:
    s2 = re.sub(r"(?:\s*\.\s*){2,}|\.{3,}", " … ", s)
    m = re.search(r"^(.*?)\s*…\s*(\d+)\s*$", s2)
    if m:
        return (
            '<div class="toc-line">'
            f'<span class="toc-title">{html.escape(m.group(1).strip())}</span>'
            '<span class="toc-dots" aria-hidden="true"></span>'
            f'<span class="toc-page">{html.escape(m.group(2))}</span>'
            "</div>"
        )
    return f'<div class="toc-line">{html.escape(s)}</div>'


def _render_def(s: str) -> str:
    m = re.match(
        r"^((?:Definition|Theorem|Lemma|Corollary|Proposition|Remark|Example|"
        r"定义|定理|引理|推论|命题|注记|备注|例子|示例)\s*\d+\.?)\s*(.*)$",
        s,
    )
    if m and m.group(2):
        return (
            '<div class="def">'
            f'<div class="def-title">{html.escape(m.group(1).rstrip("."))}</div>'
            f"<p>{html.escape(m.group(2))}</p>"
            "</div>"
        )
    return f'<div class="def"><div class="def-title">{html.escape(s)}</div></div>'


def blocks_to_html(blocks: Iterable[str]) -> str:
    out: list[str] = []
    in_list = False
    first = True

    def close_list() -> None:
        nonlocal in_list
        if in_list:
            out.append("</ul>")
            in_list = False

    for block in blocks:
        kind, s = classify(block)
        if kind == "empty":
            continue
        if kind != "li":
            close_list()

        if kind == "h1":
            out.append(f"<h1>{html.escape(s)}</h1>")
        elif kind == "h2":
            out.append(f"<h2>{html.escape(s)}</h2>")
        elif kind == "h3":
            out.append(f"<h3>{html.escape(s)}</h3>")
        elif kind == "def":
            out.append(_render_def(s))
        elif kind == "proof-label":
            out.append(f'<div class="proof-label">{html.escape(s)}</div>')
        elif kind == "li":
            if not in_list:
                out.append("<ul>")
                in_list = True
            out.append(f"<li>{html.escape(s)}</li>")
        elif kind == "toc":
            out.append(_render_toc(s))
        elif kind == "p-lead":
            out.append(_render_lead(s))
        elif kind == "math":
            out.append(f'<pre class="math">{html.escape(s)}</pre>')
        elif kind == "meta":
            out.append(f'<p class="meta-line">{html.escape(s)}</p>')
        else:
            if first and len(s) < 120 and ("Paradigm" in s or "范式" in s or "Composability" in s):
                out.append(f'<p class="paper-title">{html.escape(s)}</p>')
            else:
                out.append(f"<p>{html.escape(s)}</p>")
        first = False

    close_list()
    return "\n".join(out)


def format_page_text(text: str) -> str:
    return blocks_to_html(join_blocks(text))
