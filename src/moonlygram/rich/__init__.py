"""Rich-message construction: a builder, inline helpers, and a Markdown converter.

Bot API 10.1 rich messages are this library's headline feature. Build one with
RichMessage plus the inline helpers, or convert existing Markdown with
markdown_to_rich; either way the result feeds Bot.send_rich_message.
"""
from __future__ import annotations

from .builder import (
    Inline,
    InlineContent,
    RichMessage,
    bold,
    code,
    italic,
    link,
    mark,
    math,
    spoiler,
    strike,
    sub,
    sup,
    text,
    underline,
)
from .markdown import markdown_to_rich

__all__ = [
    "RichMessage",
    "Inline",
    "InlineContent",
    "markdown_to_rich",
    "text",
    "bold",
    "italic",
    "underline",
    "strike",
    "mark",
    "spoiler",
    "code",
    "sup",
    "sub",
    "link",
    "math",
]
