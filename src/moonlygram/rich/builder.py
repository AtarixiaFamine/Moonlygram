"""The RichMessage builder and inline-text helpers.

Bot API 10.1 rich messages are described by a small HTML dialect. RichMessage
assembles the block-level structure (headings, paragraphs, code blocks, tables,
collapsibles, math, …) and the inline helpers (bold, italic, link, …) compose
the runs of text inside a block. Everything is escaped as it is added, so plain
strings are safe to pass anywhere; use raw() for an HTML fragment you have built
yourself. Render the result with to_html() and hand it to Bot.send_rich_message.
"""
from __future__ import annotations

import html
from typing import Union

InlineContent = Union[str, "Inline"]


class Inline:
    """A run of inline rich text whose .html is already escaped and tag-wrapped."""

    __slots__ = ("html",)

    def __init__(self, html: str) -> None:
        self.html = html

    def __str__(self) -> str:
        return self.html


def _escape(text: str) -> str:
    # Telegram recognizes only &lt; &gt; &amp; &quot; — quote=False keeps ' literal.
    return html.escape(text, quote=False)


def _escape_attr(value: str) -> str:
    return html.escape(value, quote=True)


def _render(parts: tuple[InlineContent, ...]) -> str:
    """Join inline parts, escaping plain strings and passing Inline through."""
    return "".join(p.html if isinstance(p, Inline) else _escape(p) for p in parts)


def text(*parts: InlineContent) -> Inline:
    """Combine parts into one inline run (plain strings are escaped)."""
    return Inline(_render(parts))


def bold(*parts: InlineContent) -> Inline:
    """Bold inline text."""
    return Inline(f"<b>{_render(parts)}</b>")


def italic(*parts: InlineContent) -> Inline:
    """Italic inline text."""
    return Inline(f"<i>{_render(parts)}</i>")


def underline(*parts: InlineContent) -> Inline:
    """Underlined inline text."""
    return Inline(f"<u>{_render(parts)}</u>")


def strike(*parts: InlineContent) -> Inline:
    """Strikethrough inline text."""
    return Inline(f"<s>{_render(parts)}</s>")


def mark(*parts: InlineContent) -> Inline:
    """Highlighted (marked) inline text."""
    return Inline(f"<mark>{_render(parts)}</mark>")


def spoiler(*parts: InlineContent) -> Inline:
    """Spoiler-hidden inline text."""
    return Inline(f"<tg-spoiler>{_render(parts)}</tg-spoiler>")


def sup(*parts: InlineContent) -> Inline:
    """Superscript inline text."""
    return Inline(f"<sup>{_render(parts)}</sup>")


def sub(*parts: InlineContent) -> Inline:
    """Subscript inline text."""
    return Inline(f"<sub>{_render(parts)}</sub>")


def code(content: str) -> Inline:
    """Inline monospace code (literal text, not further formatted)."""
    return Inline(f"<code>{_escape(content)}</code>")


def math(expression: str) -> Inline:
    """Inline math (a tg-math expression)."""
    return Inline(f"<tg-math>{_escape(expression)}</tg-math>")


def link(content: InlineContent, url: str) -> Inline:
    """A hyperlink whose visible text is content and whose target is url."""
    return Inline(f'<a href="{_escape_attr(url)}">{_render((content,))}</a>')


class RichMessage:
    """A builder for a Bot API 10.1 rich message.

    Each method appends a block and returns self, so calls chain. Inline content
    arguments accept plain strings (escaped automatically) or Inline runs from
    the helpers in this module. Call to_html() for the payload, or pass the
    builder straight to Bot.send_rich_message.
    """

    __slots__ = ("_blocks",)

    def __init__(self) -> None:
        self._blocks: list[str] = []

    def heading(self, *content: InlineContent, level: int = 1) -> "RichMessage":
        """Add a heading; level 1 renders as h1, anything else as h2."""
        tag = "h1" if level == 1 else "h2"
        self._blocks.append(f"<{tag}>{_render(content)}</{tag}>")
        return self

    def paragraph(self, *content: InlineContent) -> "RichMessage":
        """Add a paragraph of inline content."""
        self._blocks.append(f"<p>{_render(content)}</p>")
        return self

    def quote(self, *content: InlineContent) -> "RichMessage":
        """Add a block quote."""
        self._blocks.append(f"<blockquote>{_render(content)}</blockquote>")
        return self

    def code_block(self, content: str, *, language: str | None = None) -> "RichMessage":
        """Add a fenced code block, optionally tagged with a language."""
        cls = f' class="language-{_escape_attr(language)}"' if language else ""
        self._blocks.append(f"<pre><code{cls}>{_escape(content)}</code></pre>")
        return self

    def math_block(self, expression: str) -> "RichMessage":
        """Add a centered block-math expression."""
        self._blocks.append(f"<tg-math-block>{_escape(expression)}</tg-math-block>")
        return self

    def rule(self) -> "RichMessage":
        """Add a horizontal rule."""
        self._blocks.append("<hr/>")
        return self

    def table(
        self,
        header: list[InlineContent],
        rows: list[list[InlineContent]],
    ) -> "RichMessage":
        """Add a bordered, striped table from a header row and data rows.

        Rows shorter than the header are padded with empty cells; extra cells
        beyond the header width are dropped.
        """
        width = len(header)
        head = "".join(f"<th>{_render((cell,))}</th>" for cell in header)
        body = ""
        for row in rows:
            cells = list(row[:width]) + [""] * max(0, width - len(row))
            body += "<tr>" + "".join(f"<td>{_render((cell,))}</td>" for cell in cells) + "</tr>"
        self._blocks.append(f"<table bordered striped><tr>{head}</tr>{body}</table>")
        return self

    def collapsible(
        self,
        summary: InlineContent,
        body: "RichMessage",
        *,
        expanded: bool = False,
    ) -> "RichMessage":
        """Add a collapsible section (details/summary) wrapping a nested message."""
        attr = " open" if expanded else ""
        self._blocks.append(
            f"<details{attr}><summary>{_render((summary,))}</summary>"
            f"{body.to_html()}</details>"
        )
        return self

    def footer(self, *content: InlineContent) -> "RichMessage":
        """Add a footer line."""
        self._blocks.append(f"<footer>{_render(content)}</footer>")
        return self

    def raw(self, html_fragment: str) -> "RichMessage":
        """Append a pre-built HTML fragment verbatim (escape hatch; not escaped)."""
        self._blocks.append(html_fragment)
        return self

    def to_html(self) -> str:
        """Render the accumulated blocks to the rich-message HTML string."""
        return "".join(self._blocks)

    def __str__(self) -> str:
        return self.to_html()
