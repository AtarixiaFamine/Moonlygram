"""Tests for the helpers module."""
from __future__ import annotations

import pytest

from moonlygram import (
    helpers,
    Message,
)
from moonlygram.types import Chat
from conftest import (
    _msg,
    _update,
)


def test_escape_markdown_v1_and_v2():
    assert helpers.escape_markdown("a_b*c") == r"a\_b\*c"
    assert helpers.escape_markdown("a.b!", version=2) == r"a\.b\!"
    # inside a code block only backtick and backslash are special
    assert helpers.escape_markdown("a.b`c", version=2, entity_type="pre") == r"a.b\`c"


def test_mention_html_escapes_name():
    assert helpers.mention_html(42, "A & B") == '<a href="tg://user?id=42">A &amp; B</a>'


def test_mention_markdown_versions():
    assert helpers.mention_markdown(42, "Bob") == "[Bob](tg://user?id=42)"
    assert helpers.mention_markdown(42, "a.b", version=2) == r"[a\.b](tg://user?id=42)"


def test_create_deep_linked_url():
    assert helpers.create_deep_linked_url("mybot") == "https://t.me/mybot"
    assert (
        helpers.create_deep_linked_url("mybot", "ref123")
        == "https://t.me/mybot?start=ref123"
    )
    assert (
        helpers.create_deep_linked_url("mybot", "ref123", group=True)
        == "https://t.me/mybot?startgroup=ref123"
    )
    with pytest.raises(ValueError):
        helpers.create_deep_linked_url("ab")  # too short
    with pytest.raises(ValueError):
        helpers.create_deep_linked_url("mybot", "x" * 65)  # too long
    with pytest.raises(ValueError):
        helpers.create_deep_linked_url("mybot", "bad payload!")  # bad chars


def test_effective_message_type():
    assert helpers.effective_message_type(_msg("hi")) == "text"
    photo = Message(message_id=1, chat=Chat(id=1, type="private"), photo=[])
    # an empty list is still "present" — photo wins
    assert helpers.effective_message_type(_update(photo)) == "photo"
    blank = Message(message_id=1, chat=Chat(id=1, type="private"))
    assert helpers.effective_message_type(blank) is None
