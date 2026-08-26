"""Tests for media uploads and parsing."""
from __future__ import annotations

import io
from typing import Any

import httpx

from moonlygram import (
    InputFile,
    InputMediaPhoto,
    Message,
)
from moonlygram.ext import (
    filters,
)
from conftest import (
    _MESSAGE_DICT,
    _msg,
    fake_bot,
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


async def test_send_live_photo_uploads_both_parts():
    from moonlygram import EphemeralMessageParameters

    bot, session = fake_bot(_MESSAGE_DICT)
    await bot.send_live_photo(
        5,
        InputFile(b"video", "clip.mp4"),
        "photo_file_id",
        caption="live",
        ephemeral_message_parameters=EphemeralMessageParameters(receiver_user_id=9),
    )
    method, params = session.calls[0]
    assert method == "sendLivePhoto"
    assert isinstance(params["live_photo"], InputFile)
    assert params["photo"] == "photo_file_id"
    assert params["caption"] == "live"
    assert params["ephemeral_message_parameters"] == {"receiver_user_id": 9}


def test_message_parses_a_live_photo():
    msg = Message.from_dict(
        {
            "message_id": 1,
            "chat": {"id": 1, "type": "private"},
            "live_photo": {
                "file_id": "f",
                "file_unique_id": "u",
                "width": 4,
                "height": 3,
                "duration": 2,
                "photo": [{"file_id": "p", "file_unique_id": "pu", "width": 4, "height": 3}],
            },
        }
    )
    assert msg.live_photo is not None
    assert (msg.live_photo.duration, msg.live_photo.width) == (2, 4)
    assert msg.live_photo.photo[0].file_id == "p"


async def test_media_group_uploads_nested_files_as_attachments():
    """A file inside a media object travels as its own part, named attach://."""
    captured: dict[str, Any] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["content_type"] = request.headers.get("content-type", "")
        captured["body"] = request.content
        return httpx.Response(200, json={"ok": True, "result": [_MESSAGE_DICT]})

    bot = mock_bot(handler)
    try:
        await bot.send_media_group(
            123,
            [
                InputMediaPhoto(InputFile(b"FIRST", filename="a.png"), caption="one"),
                InputMediaPhoto("existing_file_id"),
                InputMediaPhoto(InputFile(b"SECOND", filename="b.png")),
            ],
        )
        body = captured["body"]
        assert captured["content_type"].startswith("multipart/form-data")
        # each upload became its own distinctly named part
        assert b'name="attached0"' in body and b"a.png" in body and b"FIRST" in body
        assert b'name="attached1"' in body and b"b.png" in body and b"SECOND" in body
        # the media field references the parts and leaves the file_id alone
        assert b"attach://attached0" in body and b"attach://attached1" in body
        assert b"existing_file_id" in body
    finally:
        await bot.session.close()


async def test_edit_ephemeral_message_media_uploads_a_new_file():
    """Bot API 10.3 allows an upload here, not only a file_id or URL."""
    captured: dict[str, Any] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["content_type"] = request.headers.get("content-type", "")
        captured["body"] = request.content
        return httpx.Response(200, json={"ok": True, "result": True})

    bot = mock_bot(handler)
    try:
        ok = await bot.edit_ephemeral_message_media(
            1, 99, 7, InputMediaPhoto(InputFile(b"NEW", filename="new.png"))
        )
        assert ok is True
        body = captured["body"]
        assert captured["content_type"].startswith("multipart/form-data")
        assert b"attach://attached0" in body
        assert b"new.png" in body and b"NEW" in body
    finally:
        await bot.session.close()


async def test_a_top_level_file_and_a_nested_one_both_upload():
    captured: dict[str, Any] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["body"] = request.content
        return httpx.Response(200, json={"ok": True, "result": _MESSAGE_DICT})

    bot = mock_bot(handler)
    try:
        await bot.send_photo(
            123,
            InputFile(b"MAIN", filename="main.png"),
            reply_markup={"inline_keyboard": []},
        )
        assert b'name="photo"' in captured["body"] and b"main.png" in captured["body"]
    finally:
        await bot.session.close()


async def test_media_without_uploads_still_goes_as_json():
    captured: dict[str, Any] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["content_type"] = request.headers.get("content-type", "")
        captured["body"] = request.content
        return httpx.Response(200, json={"ok": True, "result": [_MESSAGE_DICT]})

    bot = mock_bot(handler)
    try:
        await bot.send_media_group(123, [InputMediaPhoto("file_id_only")])
        assert captured["content_type"].startswith("application/json")
        assert b"attach://" not in captured["body"]
    finally:
        await bot.session.close()
