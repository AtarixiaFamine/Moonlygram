"""Structured rich-message blocks (Bot API 10.2, extended in 10.3).

A rich message can be described either with the HTML or Markdown dialect (see
builder.py) or as a list of structured blocks. This module models the block
types so a caller can build that list explicitly and pass it to
Bot.send_rich_message via the blocks argument.

Each block is a small dataclass with a to_dict that stamps its fixed type
discriminator and drops unset optional fields. Text-bearing fields are typed as
RichText, which the Bot API allows to be a plain string, a list, or a nested
object; a string is the common case. Nested media reuses the InputMedia types
from moonlygram.types.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional, Union

from ..types import (
    InputMediaAnimation,
    InputMediaAudio,
    InputMediaDocument,
    InputMediaPhoto,
    InputMediaVideo,
    InputMediaVoiceNote,
    RichBlockCaption as RichBlockCaption,
    RichBlockTableCell as RichBlockTableCell,
    RichMessageButton as RichMessageButton,
    RichTextValue,
)

#: Formatted text of a block. The Bot API accepts a plain string, a list of
#: rich text, or a nested rich-text object; a string covers the common case.
#: Received text parses into a RichTextNode, which the alias also covers.
RichText = RichTextValue

#: The media an InputRichMessageMedia can carry (a rich message references it
#: from an html or markdown tg://…?id= link, including tg://document?id=).
InputRichMedia = Union[
    InputMediaAnimation,
    InputMediaAudio,
    InputMediaDocument,
    InputMediaPhoto,
    InputMediaVideo,
    InputMediaVoiceNote,
    dict[str, Any],
]


def _data(value: Any) -> Any:
    """Convert nested blocks and media to their dict form, recursing into lists.

    Plain strings, ints, and dicts (a RichText or a raw block) pass through
    unchanged; anything carrying a to_dict is serialized through it.
    """
    if isinstance(value, list):
        return [_data(v) for v in value]
    to_dict = getattr(value, "to_dict", None)
    return to_dict() if callable(to_dict) else value


def _prune(d: dict[str, Any]) -> dict[str, Any]:
    """Drop keys whose value is None so unset optionals stay out of the payload."""
    return {k: v for k, v in d.items() if v is not None}


@dataclass(slots=True)
class InputRichMessageMedia:
    """A media element referenced from a rich message's html or markdown text.

    id is the identifier used in the tg://photo?id=, tg://video?id=, or
    tg://audio?id= link inside the text; media carries the file itself.
    """

    id: str
    media: InputRichMedia

    def to_dict(self) -> dict[str, Any]:
        return {"id": self.id, "media": _data(self.media)}


@dataclass(slots=True)
class InputRichBlockListItem:
    """An item in a list block.

    type sets the ordered-list label style and must be "1", "a", "A", "i",
    or "I"; Telegram rejects the whole message on any other value.
    """

    blocks: list["InputRichBlock"]
    has_checkbox: Optional[bool] = None
    is_checked: Optional[bool] = None
    value: Optional[int] = None
    type: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return _prune(
            {
                "blocks": _data(self.blocks),
                "has_checkbox": self.has_checkbox,
                "is_checked": self.is_checked,
                "value": self.value,
                "type": self.type,
            }
        )


@dataclass(slots=True)
class InputRichBlockParagraph:
    """A text paragraph."""

    text: RichText

    def to_dict(self) -> dict[str, Any]:
        return {"type": "paragraph", "text": _data(self.text)}


@dataclass(slots=True)
class InputRichBlockSectionHeading:
    """A section heading. size runs 1 (largest) to 6 (smallest)."""

    text: RichText
    size: int

    def to_dict(self) -> dict[str, Any]:
        return {"type": "heading", "text": _data(self.text), "size": self.size}


@dataclass(slots=True)
class InputRichBlockPreformatted:
    """A preformatted code block, optionally tagged with a language."""

    text: RichText
    language: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return _prune(
            {"type": "pre", "text": _data(self.text), "language": self.language}
        )


@dataclass(slots=True)
class InputRichBlockFooter:
    """A footer line."""

    text: RichText

    def to_dict(self) -> dict[str, Any]:
        return {"type": "footer", "text": _data(self.text)}


@dataclass(slots=True)
class InputRichBlockDivider:
    """A horizontal divider."""

    def to_dict(self) -> dict[str, Any]:
        return {"type": "divider"}


@dataclass(slots=True)
class InputRichBlockMathematicalExpression:
    """A block mathematical expression in LaTeX format."""

    expression: str

    def to_dict(self) -> dict[str, Any]:
        return {"type": "mathematical_expression", "expression": self.expression}


@dataclass(slots=True)
class InputRichBlockAnchor:
    """A named anchor that other content can link to."""

    name: str

    def to_dict(self) -> dict[str, Any]:
        return {"type": "anchor", "name": self.name}


@dataclass(slots=True)
class InputRichBlockList:
    """An ordered or unordered list of items."""

    items: list[InputRichBlockListItem]

    def to_dict(self) -> dict[str, Any]:
        return {"type": "list", "items": _data(self.items)}


@dataclass(slots=True)
class InputRichBlockBlockQuotation:
    """A block quotation wrapping nested blocks."""

    blocks: list["InputRichBlock"]
    credit: Optional[RichText] = None

    def to_dict(self) -> dict[str, Any]:
        return _prune(
            {
                "type": "blockquote",
                "blocks": _data(self.blocks),
                "credit": _data(self.credit),
            }
        )


@dataclass(slots=True)
class InputRichBlockExpandableBlockQuotation:
    """A block quotation the reader can expand and collapse again."""

    text: RichText
    credit: Optional[RichText] = None

    def to_dict(self) -> dict[str, Any]:
        return _prune(
            {
                "type": "expandable_blockquote",
                "text": _data(self.text),
                "credit": _data(self.credit),
            }
        )


@dataclass(slots=True)
class InputRichBlockPullQuotation:
    """A pull quotation with centered text."""

    text: RichText
    credit: Optional[RichText] = None

    def to_dict(self) -> dict[str, Any]:
        return _prune(
            {"type": "pullquote", "text": _data(self.text), "credit": _data(self.credit)}
        )


@dataclass(slots=True)
class InputRichBlockCollage:
    """A collage of nested blocks."""

    blocks: list["InputRichBlock"]
    caption: Optional[RichBlockCaption] = None

    def to_dict(self) -> dict[str, Any]:
        return _prune(
            {
                "type": "collage",
                "blocks": _data(self.blocks),
                "caption": _data(self.caption),
            }
        )


@dataclass(slots=True)
class InputRichBlockSlideshow:
    """A slideshow of nested blocks."""

    blocks: list["InputRichBlock"]
    caption: Optional[RichBlockCaption] = None

    def to_dict(self) -> dict[str, Any]:
        return _prune(
            {
                "type": "slideshow",
                "blocks": _data(self.blocks),
                "caption": _data(self.caption),
            }
        )


@dataclass(slots=True)
class InputRichBlockTable:
    """A table. cells is a list of rows, each a list of RichBlockTableCell."""

    cells: list[list[RichBlockTableCell]]
    is_bordered: Optional[bool] = None
    is_striped: Optional[bool] = None
    is_compact: Optional[bool] = None
    caption: Optional[RichText] = None

    def to_dict(self) -> dict[str, Any]:
        return _prune(
            {
                "type": "table",
                "cells": _data(self.cells),
                "is_bordered": self.is_bordered,
                "is_striped": self.is_striped,
                "is_compact": self.is_compact,
                "caption": _data(self.caption),
            }
        )


@dataclass(slots=True)
class InputRichBlockDetails:
    """An expandable details block with an always-visible summary."""

    summary: RichText
    blocks: list["InputRichBlock"]
    is_open: Optional[bool] = None

    def to_dict(self) -> dict[str, Any]:
        return _prune(
            {
                "type": "details",
                "summary": _data(self.summary),
                "blocks": _data(self.blocks),
                "is_open": self.is_open,
            }
        )


@dataclass(slots=True)
class InputRichBlockMap:
    """A map centered on a location. location is a {latitude, longitude} mapping.

    The width and height must not exceed 10000 in total, with a ratio of at
    most 20.
    """

    location: dict[str, Any]
    zoom: int
    width: int
    height: int
    caption: Optional[RichBlockCaption] = None

    def to_dict(self) -> dict[str, Any]:
        return _prune(
            {
                "type": "map",
                "location": _data(self.location),
                "zoom": self.zoom,
                "width": self.width,
                "height": self.height,
                "caption": _data(self.caption),
            }
        )


@dataclass(slots=True)
class InputRichBlockAnimation:
    """A block holding an animation. The media's own caption is ignored."""

    animation: Union[InputMediaAnimation, dict[str, Any]]
    caption: Optional[RichBlockCaption] = None

    def to_dict(self) -> dict[str, Any]:
        return _prune(
            {
                "type": "animation",
                "animation": _data(self.animation),
                "caption": _data(self.caption),
            }
        )


@dataclass(slots=True)
class InputRichBlockAudio:
    """A block holding a music file. The media's own caption is ignored."""

    audio: Union[InputMediaAudio, dict[str, Any]]
    caption: Optional[RichBlockCaption] = None

    def to_dict(self) -> dict[str, Any]:
        return _prune(
            {
                "type": "audio",
                "audio": _data(self.audio),
                "caption": _data(self.caption),
            }
        )


@dataclass(slots=True)
class InputRichBlockPhoto:
    """A block holding a photo. The media's own caption is ignored."""

    photo: Union[InputMediaPhoto, dict[str, Any]]
    caption: Optional[RichBlockCaption] = None

    def to_dict(self) -> dict[str, Any]:
        return _prune(
            {
                "type": "photo",
                "photo": _data(self.photo),
                "caption": _data(self.caption),
            }
        )


@dataclass(slots=True)
class InputRichBlockVideo:
    """A block holding a video. The media's own caption is ignored."""

    video: Union[InputMediaVideo, dict[str, Any]]
    caption: Optional[RichBlockCaption] = None

    def to_dict(self) -> dict[str, Any]:
        return _prune(
            {
                "type": "video",
                "video": _data(self.video),
                "caption": _data(self.caption),
            }
        )


@dataclass(slots=True)
class InputRichBlockVoiceNote:
    """A block holding a voice note. The media's own caption is ignored."""

    voice_note: Union[InputMediaVoiceNote, dict[str, Any]]
    caption: Optional[RichBlockCaption] = None

    def to_dict(self) -> dict[str, Any]:
        return _prune(
            {
                "type": "voice_note",
                "voice_note": _data(self.voice_note),
                "caption": _data(self.caption),
            }
        )


@dataclass(slots=True)
class InputRichBlockDocument:
    """A block holding a general file. The media's own caption is ignored.

    A rich message may also reference an uploaded file from its html or
    markdown text with a tg://document?id= link.
    """

    document: Union[InputMediaDocument, dict[str, Any]]
    caption: Optional[RichBlockCaption] = None

    def to_dict(self) -> dict[str, Any]:
        return _prune(
            {
                "type": "document",
                "document": _data(self.document),
                "caption": _data(self.caption),
            }
        )


@dataclass(slots=True)
class InputRichBlockButtons:
    """A row of 1-8 buttons. align is "left", "center", or "right"."""

    buttons: list[RichMessageButton]
    align: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return _prune(
            {
                "type": "buttons",
                "buttons": _data(self.buttons),
                "align": self.align,
            }
        )


@dataclass(slots=True)
class InputRichBlockThinking:
    """A "Thinking…" placeholder. Valid only in send_rich_message_draft."""

    text: RichText

    def to_dict(self) -> dict[str, Any]:
        return {"type": "thinking", "text": _data(self.text)}


#: Any block usable in a rich message's blocks list (or a raw dict for one this
#: library does not model yet).
InputRichBlock = Union[
    InputRichBlockParagraph,
    InputRichBlockSectionHeading,
    InputRichBlockPreformatted,
    InputRichBlockFooter,
    InputRichBlockDivider,
    InputRichBlockMathematicalExpression,
    InputRichBlockAnchor,
    InputRichBlockList,
    InputRichBlockBlockQuotation,
    InputRichBlockExpandableBlockQuotation,
    InputRichBlockPullQuotation,
    InputRichBlockCollage,
    InputRichBlockSlideshow,
    InputRichBlockTable,
    InputRichBlockDetails,
    InputRichBlockMap,
    InputRichBlockAnimation,
    InputRichBlockAudio,
    InputRichBlockPhoto,
    InputRichBlockVideo,
    InputRichBlockVoiceNote,
    InputRichBlockDocument,
    InputRichBlockButtons,
    InputRichBlockThinking,
    dict[str, Any],
]
