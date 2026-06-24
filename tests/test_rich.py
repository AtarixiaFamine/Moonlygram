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
