"""Tests for rich messages."""
from __future__ import annotations

import pytest

from moonlygram import (
    Message,
)
from conftest import (
    _MESSAGE_DICT,
    fake_bot,
)


def test_rich_inline_helpers_escape_and_nest():
    from moonlygram.rich import bold, code, italic, mark, math, spoiler

    assert bold("a<b>").html == "<b>a&lt;b&gt;</b>"
    assert italic("x").html == "<i>x</i>"
    assert bold("hi ", italic("there")).html == "<b>hi <i>there</i></b>"
    assert code("a < b").html == "<code>a &lt; b</code>"
    assert spoiler("boo").html == "<tg-spoiler>boo</tg-spoiler>"
    assert math("E=mc^2").html == "<tg-math>E=mc^2</tg-math>"
    assert mark("hl").html == "<mark>hl</mark>"


def test_rich_link_escapes_url_and_text():
    from moonlygram.rich import bold, link

    assert link("click", 'a"b').html == '<a href="a&quot;b">click</a>'
    assert link(bold("here"), "https://x.io").html == (
        '<a href="https://x.io"><b>here</b></a>'
    )


def test_rich_message_builder_blocks():
    from moonlygram.rich import RichMessage, bold

    msg = (
        RichMessage()
        .heading("T")
        .heading("S", level=2)
        .paragraph("hi ", bold("you"))
        .code_block("x=1", language="python")
        .math_block("a+b")
        .quote("q")
        .rule()
        .footer("f")
    )
    rendered = msg.to_html()
    assert "<h1>T</h1>" in rendered
    assert "<h2>S</h2>" in rendered
    assert "<p>hi <b>you</b></p>" in rendered
    assert '<pre><code class="language-python">x=1</code></pre>' in rendered
    assert "<tg-math-block>a+b</tg-math-block>" in rendered
    assert "<blockquote>q</blockquote>" in rendered
    assert "<hr/>" in rendered
    assert "<footer>f</footer>" in rendered
    assert str(msg) == rendered


def test_rich_code_block_escapes_without_language():
    from moonlygram.rich import RichMessage

    out = RichMessage().code_block("a < b & c").to_html()
    assert out == "<pre><code>a &lt; b &amp; c</code></pre>"


def test_rich_table_pads_and_truncates():
    from moonlygram.rich import RichMessage

    out = RichMessage().table(["A", "B"], [["1", "2", "3"], ["x"]]).to_html()
    assert "<tr><th>A</th><th>B</th></tr>" in out
    assert "<tr><td>1</td><td>2</td></tr>" in out  # extra cell dropped
    assert "<tr><td>x</td><td></td></tr>" in out  # short row padded


def test_rich_collapsible_nests_message():
    from moonlygram.rich import RichMessage

    body = RichMessage().paragraph("inside")
    out = RichMessage().collapsible("Show", body, expanded=True).to_html()
    assert out == "<details open><summary>Show</summary><p>inside</p></details>"
    closed = RichMessage().collapsible("Hide", RichMessage().paragraph("x")).to_html()
    assert closed == "<details><summary>Hide</summary><p>x</p></details>"


def test_rich_raw_passthrough():
    from moonlygram.rich import RichMessage

    assert RichMessage().raw("<custom>x</custom>").to_html() == "<custom>x</custom>"


def test_markdown_to_rich_conversions():
    from moonlygram import markdown_to_rich

    assert markdown_to_rich("# Title") == "<h1>Title</h1>"
    assert markdown_to_rich("a **b** c") == "<p>a <b>b</b> c</p>"
    assert markdown_to_rich("use `x` here") == "<p>use <code>x</code> here</p>"
    assert markdown_to_rich("[t](http://u)") == '<p><a href="http://u">t</a></p>'
    assert markdown_to_rich("```python\nprint(1)\n```") == (
        '<pre><code class="language-python">print(1)\n</code></pre>'
    )


def test_markdown_to_rich_table():
    from moonlygram import markdown_to_rich

    out = markdown_to_rich("| A | B |\n| - | - |\n| 1 | 2 |")
    assert out == (
        "<table bordered striped><tr><th>A</th><th>B</th></tr>"
        "<tr><td>1</td><td>2</td></tr></table>"
    )


def test_markdown_to_rich_table_cells_format_inline():
    from moonlygram import markdown_to_rich

    out = markdown_to_rich(
        "| Country | GDP |\n| - | - |\n| **Germany** | [src](http://u) |"
    )
    assert out == (
        "<table bordered striped>"
        "<tr><th>Country</th><th>GDP</th></tr>"
        '<tr><td><b>Germany</b></td><td><a href="http://u">src</a></td></tr>'
        "</table>"
    )


def test_markdown_to_rich_table_cell_br_becomes_break():
    from moonlygram import markdown_to_rich

    # <br> is the GitHub-table idiom for an in-cell line break; every spelling
    # (and case) becomes the renderer's own <br/>, not literal &lt;br&gt; text.
    out = markdown_to_rich(
        "| Role | Notes |\n| - | - |\n| DPS<br>Energy | a<br/>b<BR />c |"
    )
    assert out == (
        "<table bordered striped>"
        "<tr><th>Role</th><th>Notes</th></tr>"
        "<tr><td>DPS<br/>Energy</td><td>a<br/>b<br/>c</td></tr>"
        "</table>"
    )


def test_markdown_to_rich_table_math_does_not_span_columns():
    from moonlygram import markdown_to_rich

    # Each cell keeps its own math; the column delimiter is never swallowed.
    out = markdown_to_rich("| A | B |\n| - | - |\n| $4.686$ | $5.014$ |")
    assert out == (
        "<table bordered striped><tr><th>A</th><th>B</th></tr>"
        "<tr><td><tg-math>4.686</tg-math></td>"
        "<td><tg-math>5.014</tg-math></td></tr></table>"
    )


async def test_send_rich_message_with_builder():
    from moonlygram.rich import RichMessage, bold

    bot, session = fake_bot(_MESSAGE_DICT)
    result = await bot.send_rich_message(1, html=RichMessage().paragraph("Hi ", bold("there")))
    assert isinstance(result, Message)
    method, params = session.calls[0]
    assert method == "sendRichMessage"
    assert params["chat_id"] == 1
    assert params["rich_message"] == {"html": "<p>Hi <b>there</b></p>"}


async def test_send_rich_message_markdown_param():
    bot, session = fake_bot(_MESSAGE_DICT)
    await bot.send_rich_message(1, markdown="# Hi")
    _, params = session.calls[0]
    assert params["rich_message"] == {"markdown": "# Hi"}


async def test_send_rich_message_draft_params():
    from moonlygram.rich import RichMessage

    bot, session = fake_bot(True)
    ok = await bot.send_rich_message_draft(
        5, 1234, html=RichMessage().paragraph("streaming")
    )
    assert ok is True
    method, params = session.calls[0]
    assert method == "sendRichMessageDraft"
    assert params == {
        "chat_id": 5,
        "draft_id": 1234,
        "rich_message": {"html": "<p>streaming</p>"},
    }


async def test_send_rich_message_draft_requires_one_format():
    bot, _ = fake_bot()
    with pytest.raises(ValueError):
        await bot.send_rich_message_draft(1, 2)


def test_rich_block_paragraph_and_heading_to_dict():
    from moonlygram.rich import InputRichBlockParagraph, InputRichBlockSectionHeading

    assert InputRichBlockParagraph("hi").to_dict() == {"type": "paragraph", "text": "hi"}
    assert InputRichBlockSectionHeading("T", size=1).to_dict() == {
        "type": "heading",
        "text": "T",
        "size": 1,
    }


def test_rich_block_list_nests_items():
    from moonlygram.rich import (
        InputRichBlockList,
        InputRichBlockListItem,
        InputRichBlockParagraph,
    )

    block = InputRichBlockList(
        items=[InputRichBlockListItem(blocks=[InputRichBlockParagraph("a")], value=1)]
    )
    assert block.to_dict() == {
        "type": "list",
        "items": [{"blocks": [{"type": "paragraph", "text": "a"}], "value": 1}],
    }


def test_rich_block_table_nests_cells_and_prunes():
    from moonlygram.rich import InputRichBlockTable, RichBlockTableCell

    table = InputRichBlockTable(
        cells=[[RichBlockTableCell(text="A", is_header=True), RichBlockTableCell()]],
        is_bordered=True,
    )
    assert table.to_dict() == {
        "type": "table",
        "cells": [[{"text": "A", "is_header": True}, {}]],
        "is_bordered": True,
    }


def test_rich_block_photo_serializes_inner_media():
    from moonlygram import InputMediaPhoto
    from moonlygram.rich import InputRichBlockPhoto, RichBlockCaption

    block = InputRichBlockPhoto(InputMediaPhoto("file1"), caption=RichBlockCaption(text="cap"))
    assert block.to_dict() == {
        "type": "photo",
        "photo": {"type": "photo", "media": "file1"},
        "caption": {"text": "cap"},
    }


def test_input_rich_message_media_to_dict():
    from moonlygram import InputMediaVideo
    from moonlygram.rich import InputRichMessageMedia

    media = InputRichMessageMedia(id="v1", media=InputMediaVideo("file2"))
    assert media.to_dict() == {"id": "v1", "media": {"type": "video", "media": "file2"}}


async def test_send_rich_message_with_blocks():
    from moonlygram.rich import InputRichBlockParagraph

    bot, session = fake_bot(_MESSAGE_DICT)
    result = await bot.send_rich_message(1, blocks=[InputRichBlockParagraph("Hi")])
    assert isinstance(result, Message)
    method, params = session.calls[0]
    assert method == "sendRichMessage"
    assert params["rich_message"] == {"blocks": [{"type": "paragraph", "text": "Hi"}]}


async def test_send_rich_message_with_media():
    from moonlygram import InputMediaPhoto
    from moonlygram.rich import InputRichMessageMedia

    bot, session = fake_bot(_MESSAGE_DICT)
    await bot.send_rich_message(
        1,
        markdown="![](tg://photo?id=p1)",
        media=[InputRichMessageMedia(id="p1", media=InputMediaPhoto("file9"))],
    )
    _, params = session.calls[0]
    assert params["rich_message"] == {
        "markdown": "![](tg://photo?id=p1)",
        "media": [{"id": "p1", "media": {"type": "photo", "media": "file9"}}],
    }


async def test_send_rich_message_blocks_conflicts_with_other_forms():
    from moonlygram.rich import InputRichBlockParagraph

    bot, _ = fake_bot()
    with pytest.raises(ValueError):
        await bot.send_rich_message(
            1, html="<p>x</p>", blocks=[InputRichBlockParagraph("y")]
        )


def test_buttons_block_serializes_a_row():
    from moonlygram import DisabledButton
    from moonlygram.rich import InputRichBlockButtons, RichMessageButton

    block = InputRichBlockButtons(
        [
            RichMessageButton("Open", url="https://example.com", style="link"),
            RichMessageButton("Soon", disabled=DisabledButton()),
        ],
        align="center",
    )
    assert block.to_dict() == {
        "type": "buttons",
        "buttons": [
            {"text": "Open", "style": "link", "url": "https://example.com"},
            {"text": "Soon", "disabled": {}},
        ],
        "align": "center",
    }


def test_document_block_carries_its_media():
    from moonlygram import InputMediaDocument
    from moonlygram.rich import InputRichBlockDocument, RichBlockCaption

    block = InputRichBlockDocument(
        InputMediaDocument("file9"), caption=RichBlockCaption("report")
    )
    assert block.to_dict() == {
        "type": "document",
        "document": {"type": "document", "media": "file9"},
        "caption": {"text": "report"},
    }


def test_expandable_block_quotation_uses_its_own_discriminator():
    from moonlygram.rich import (
        InputRichBlockBlockQuotation,
        InputRichBlockExpandableBlockQuotation,
        InputRichBlockParagraph,
    )

    plain = InputRichBlockBlockQuotation([InputRichBlockParagraph("q")])
    expandable = InputRichBlockExpandableBlockQuotation("q", credit="me")
    assert plain.to_dict()["type"] == "blockquote"
    assert expandable.to_dict() == {
        "type": "expandable_blockquote",
        "text": "q",
        "credit": "me",
    }


def test_table_is_compact_is_omitted_when_unset():
    from moonlygram.rich import InputRichBlockTable, RichBlockTableCell

    cells = [[RichBlockTableCell("a")]]
    assert "is_compact" not in InputRichBlockTable(cells).to_dict()
    assert InputRichBlockTable(cells, is_compact=True).to_dict()["is_compact"] is True


async def test_buttons_block_reaches_the_wire_through_send_rich_message():
    from moonlygram.rich import InputRichBlockButtons, RichMessageButton

    bot, session = fake_bot(_MESSAGE_DICT)
    await bot.send_rich_message(
        1, blocks=[InputRichBlockButtons([RichMessageButton("Go", callback_data="go")])]
    )
    _, params = session.calls[0]
    assert params["rich_message"]["blocks"] == [
        {"type": "buttons", "buttons": [{"text": "Go", "callback_data": "go"}]}
    ]


def test_rich_message_media_carries_a_document():
    """10.3 added tg://document?id= links, so documents are referenceable media."""
    from moonlygram import InputMediaDocument
    from moonlygram.rich import InputRichMessageMedia

    media = InputRichMessageMedia("doc1", InputMediaDocument("file9"))
    assert media.to_dict() == {
        "id": "doc1",
        "media": {"type": "document", "media": "file9"},
    }


_RECEIVED = {
    "is_rtl": False,
    "blocks": [
        {"type": "paragraph", "text": [{"type": "bold", "text": "Hi"}, " there"]},
        {
            "type": "table",
            "cells": [[{"text": "a", "is_header": True}]],
            "is_compact": True,
            "caption": "a plain caption",
        },
        {
            "type": "photo",
            "photo": [{"file_id": "f", "file_unique_id": "u", "width": 1, "height": 1}],
            "caption": {"text": "shot", "credit": "me"},
        },
        {
            "type": "buttons",
            "buttons": [{"text": "Go", "url": "https://x", "disabled": {}}],
            "align": "center",
        },
        {"type": "expandable_blockquote", "text": "long", "credit": "me"},
    ],
}


def _received_blocks():
    from moonlygram import Message

    msg = Message.from_dict(
        {"message_id": 1, "chat": {"id": 1, "type": "private"}, "rich_message": _RECEIVED}
    )
    assert msg.rich_message is not None
    return msg.rich_message


def test_received_rich_message_parses_its_blocks():
    rich = _received_blocks()
    assert rich.is_rtl is False
    assert [b.type for b in rich.blocks] == [
        "paragraph",
        "table",
        "photo",
        "buttons",
        "expandable_blockquote",
    ]


def test_received_rich_text_mixes_nodes_and_plain_strings():
    from moonlygram import RichTextNode

    paragraph = _received_blocks().blocks[0]
    node, plain = paragraph.text
    assert isinstance(node, RichTextNode)
    assert (node.type, node.text) == ("bold", "Hi")
    assert plain == " there"  # a bare string stays a string


def test_caption_parses_by_shape_not_by_field_name():
    """A table captions with RichText, a media block with RichBlockCaption."""
    from moonlygram.rich import RichBlockCaption

    table, photo = _received_blocks().blocks[1], _received_blocks().blocks[2]
    assert table.caption == "a plain caption"
    assert isinstance(photo.caption, RichBlockCaption)
    assert (photo.caption.text, photo.caption.credit) == ("shot", "me")
    assert table.is_compact is True
    assert table.cells[0][0].is_header is True


def test_received_buttons_carry_the_disabled_marker():
    from moonlygram import DisabledButton

    buttons = _received_blocks().blocks[3]
    assert buttons.align == "center"
    button = buttons.buttons[0]
    assert (button.text, button.url) == ("Go", "https://x")
    assert button.disabled == DisabledButton()


def test_rich_message_button_round_trips():
    from moonlygram.rich import RichMessageButton

    sent = RichMessageButton("Go", callback_data="g", style="primary")
    assert RichMessageButton.from_dict(sent.to_dict()) == sent
