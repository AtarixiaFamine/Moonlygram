"""Tests for media uploads and parsing."""
from __future__ import annotations

import io
from typing import Any

import httpx

from moonlygram import (
    InputFile,
    Message,
)
from moonlygram.ext import (
    filters,
)
from conftest import (
    _MESSAGE_DICT,
    _msg,
    mock_bot,
)


def test_inputfile_from_bytes_path_and_stream(tmp_path):
    from_bytes = InputFile(b"data", filename="x.bin")
    assert from_bytes.content == b"data" and from_bytes.filename == "x.bin"

    path = tmp_path / "hello.txt"
    path.write_bytes(b"hi there")
    from_path = InputFile(str(path))
    assert from_path.content == b"hi there" and from_path.filename == "hello.txt"

    from_stream = InputFile(io.BytesIO(b"buf"), filename="b.dat")
    assert from_stream.content == b"buf" and from_stream.filename == "b.dat"


def test_message_parses_media():
    raw = {
        "message_id": 1,
        "chat": {"id": 1, "type": "private"},
        "caption": "look",
        "photo": [{"file_id": "p1", "file_unique_id": "u1", "width": 90, "height": 90}],
        "document": {"file_id": "d1", "file_unique_id": "du1", "file_name": "a.pdf"},
    }
    msg = Message.from_dict(raw)
    assert msg.caption == "look"
    assert msg.photo is not None and msg.photo[0].file_id == "p1"
    assert msg.document is not None and msg.document.file_name == "a.pdf"


def test_media_filters():
    photo_msg = Message.from_dict(
        {
            "message_id": 1,
            "chat": {"id": 1, "type": "private"},
            "photo": [{"file_id": "p", "file_unique_id": "u", "width": 1, "height": 1}],
        }
    )
    assert filters.photo(photo_msg)
    assert not filters.photo(_msg("hi"))
    assert not filters.document(photo_msg)


async def test_send_photo_uploads_inputfile_as_multipart():
    captured: dict[str, Any] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["content_type"] = request.headers.get("content-type", "")
        captured["body"] = request.content
        return httpx.Response(200, json={"ok": True, "result": _MESSAGE_DICT})

    bot = mock_bot(handler)
    try:
        msg = await bot.send_photo(123, InputFile(b"PNGBYTES", filename="pic.png"), caption="hi")
        assert isinstance(msg, Message)
        assert captured["content_type"].startswith("multipart/form-data")
        body = captured["body"]
        assert b"pic.png" in body and b"PNGBYTES" in body
        assert b'name="caption"' in body and b"hi" in body
        assert b'name="chat_id"' in body and b"123" in body
    finally:
        await bot.session.close()


async def test_send_photo_with_file_id_uses_json():
    captured: dict[str, Any] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["content_type"] = request.headers.get("content-type", "")
        captured["body"] = request.content
        return httpx.Response(200, json={"ok": True, "result": _MESSAGE_DICT})

    bot = mock_bot(handler)
    try:
        await bot.send_photo(123, "AgACAgID-file-id")
        assert captured["content_type"].startswith("application/json")
        assert b"AgACAgID-file-id" in captured["body"]
    finally:
        await bot.session.close()


async def test_get_file_then_download():
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/getFile"):
            return httpx.Response(
                200,
                json={
                    "ok": True,
                    "result": {"file_id": "f", "file_unique_id": "u", "file_path": "photos/x.jpg"},
                },
            )
        assert request.url.path.endswith("/photos/x.jpg")
        return httpx.Response(200, content=b"IMG")

    bot = mock_bot(handler)
    try:
        file = await bot.get_file("f")
        assert file.file_path == "photos/x.jpg"
        assert await bot.download_file(file.file_path) == b"IMG"
    finally:
        await bot.session.close()
