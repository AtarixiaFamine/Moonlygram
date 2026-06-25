"""Convert Markdown to Bot API 10.1 rich-message HTML.

This turns the Markdown that an LLM (or a person) tends to produce into the rich
HTML dialect Bot.send_rich_message accepts: fenced code, inline code, math,
tables, headings, rules, block quotes, lists, emphasis, and links. Code and math
spans are stashed before the rest is escaped so their contents stay literal.

Some constructs map to plain text on purpose: bullet and numbered lists become
prefixed lines (no list tags), and triple emphasis is not special-cased. Anything
the renderer does not support simply shows as text, which is the safe fallback.

Table cells run through the same inline pipeline as ordinary text, so emphasis,
math and links work inside them. The split into cells happens before math and
emphasis are applied, so a span can never leak across a column delimiter.
"""
from __future__ import annotations

import html
import re
import uuid
from typing import Callable


def markdown_to_rich(text: str) -> str:
    """Convert a Markdown string to rich-message HTML."""
    placeholders: dict[str, str] = {}

    def stash(value: str) -> str:
        key = f"\x00{uuid.uuid4().hex}\x00"
        placeholders[key] = value
        return key

    # Fenced code blocks: ```lang\n...\n```
    def repl_fence(m: "re.Match[str]") -> str:
        lang = m.group(1) or ""
        body = html.escape(m.group(2), quote=False)
        cls = f' class="language-{html.escape(lang, quote=False)}"' if lang else ""
        return stash(f"<pre><code{cls}>{body}</code></pre>")

    text = re.sub(r"```(\w+)?\n(.*?)```", repl_fence, text, flags=re.S)

    # Inline code: `...`  Stashed before tables so a `value | with a pipe` span is
    # not mistaken for a column break.
    text = re.sub(
        r"`([^`\n]+)`",
        lambda m: stash(f"<code>{html.escape(m.group(1), quote=False)}</code>"),
        text,
    )

    # GitHub-style tables → <table bordered striped>. Cells are rendered through
    # the inline pipeline here — before the document-wide math and emphasis passes
    # run — so a span cannot leak across a column delimiter.
    text = _convert_tables(text, stash)

    # Math outside table cells: block $$...$$ then inline $...$.
    text = _stash_math(text, stash)

    # Escape whatever text is left before adding our own tags.
    text = html.escape(text, quote=False)

    # Headings — match more hashes before fewer so ### does not eat #.
    text = re.sub(r"^###+ +(.*)$", r"<h2>\1</h2>", text, flags=re.M)
    text = re.sub(r"^## +(.*)$", r"<h2>\1</h2>", text, flags=re.M)
    text = re.sub(r"^# +(.*)$", r"<h1>\1</h1>", text, flags=re.M)

    # Horizontal rule
    text = re.sub(r"^(-{3,}|\*{3,}|_{3,})$", "<hr/>", text, flags=re.M)

    # Block quote (the '>' was escaped to '&gt;' above).
    text = re.sub(r"^&gt; ?(.*)$", r"<blockquote>\1</blockquote>", text, flags=re.M)

    # Bullet / numbered lists → plain prefixed lines (no list-tag support assumed).
    text = re.sub(r"^[-*+] +(.*)$", r"• \1", text, flags=re.M)
    text = re.sub(r"^(\d+)\. +(.*)$", r"\1. \2", text, flags=re.M)

    # Emphasis, strike, spoiler and links.
    text = _inline_format(text)

    # Wrap loose text in <p>. Blocks that are already block-level (a heading,
    # rule, quote, or a stashed placeholder) are emitted as-is.
    blocks = re.split(r"\n\s*\n", text)
    rendered: list[str] = []
    for block in blocks:
        block = block.strip("\n")
        if not block:
            continue
        if re.match(r"^(<h1>|<h2>|<hr/>|<blockquote>|\x00)", block):
            rendered.append(block.replace("\n", "<br/>"))
        else:
            rendered.append(f"<p>{block.replace(chr(10), '<br/>')}</p>")
    text = "".join(rendered)

    # Restore stashed blocks, outermost first so a table is expanded before the
    # inline code/math that may sit inside one of its cells.
    for key in reversed(list(placeholders)):
        text = text.replace(key, placeholders[key])

    return text


def _stash_math(text: str, stash: Callable[[str], str]) -> str:
    """Replace $$...$$ and $...$ spans with stashed math elements."""
    text = re.sub(
        r"\$\$(.+?)\$\$",
        lambda m: stash(
            f"<tg-math-block>{html.escape(m.group(1).strip(), quote=False)}</tg-math-block>"
        ),
        text,
        flags=re.S,
    )
    text = re.sub(
        r"\$([^\$\n]+)\$",
        lambda m: stash(f"<tg-math>{html.escape(m.group(1), quote=False)}</tg-math>"),
        text,
    )
    return text


def _inline_format(text: str) -> str:
    """Apply emphasis, strike, spoiler and links to already-escaped text."""
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"__(.+?)__", r"<b>\1</b>", text)
    text = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<i>\1</i>", text)
    text = re.sub(r"(?<!_)_(?!_)(.+?)(?<!_)_(?!_)", r"<i>\1</i>", text)
    text = re.sub(r"~~(.+?)~~", r"<s>\1</s>", text)
    text = re.sub(r"\|\|(.+?)\|\|", r"<tg-spoiler>\1</tg-spoiler>", text)
    text = re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2">\1</a>', text)
    return text


def _render_cell(cell: str, stash: Callable[[str], str]) -> str:
    """Render one table cell's inline Markdown to rich HTML.

    Inline code was already stashed before the table was parsed; here we stash
    math literally, escape the rest, then apply emphasis and links.
    """
    cell = _stash_math(cell, stash)
    cell = html.escape(cell, quote=False)
    return _inline_format(cell)


def _convert_tables(text: str, stash: Callable[[str], str]) -> str:
    """Replace GitHub-style Markdown tables with stashed <table> HTML."""
    lines = text.split("\n")
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if (
            "|" in line
            and i + 1 < len(lines)
            and "-" in lines[i + 1]
            and re.match(r"^\s*\|?[\s:|-]+\|?\s*$", lines[i + 1])
        ):
            header = [c.strip() for c in line.strip().strip("|").split("|")]
            j = i + 2
            rows: list[list[str]] = []
            while j < len(lines) and "|" in lines[j]:
                rows.append([c.strip() for c in lines[j].strip().strip("|").split("|")])
                j += 1

            head_html = "".join(f"<th>{_render_cell(c, stash)}</th>" for c in header)
            body_html = ""
            for row in rows:
                cells = row[: len(header)] + [""] * max(0, len(header) - len(row))
                body_html += (
                    "<tr>"
                    + "".join(f"<td>{_render_cell(c, stash)}</td>" for c in cells)
                    + "</tr>"
                )
            out.append(
                stash(
                    f"<table bordered striped><tr>{head_html}</tr>{body_html}</table>"
                )
            )
            i = j
        else:
            out.append(line)
            i += 1
    return "\n".join(out)
