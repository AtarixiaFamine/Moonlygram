"""Tests for sticker-set management."""
from __future__ import annotations

from typing import Any

import httpx

from moonlygram import (
    InputFile,
    InputSticker,
    MaskPosition,
    StickerSet,
)
from conftest import (
    fake_bot,
    mock_bot,
)


def test_input_sticker_and_mask_position_to_dict():
    sticker = InputSticker(
        "file_id_1",
        format="static",
        emoji_list=["\N{DOG FACE}"],
        mask_position=MaskPosition("forehead", 0.0, 0.1, 2.0),
        keywords=["dog"],
    )
    assert sticker.to_dict() == {
        "sticker": "file_id_1",
        "format": "static",
        "emoji_list": ["\N{DOG FACE}"],
        "mask_position": {"point": "forehead", "x_shift": 0.0, "y_shift": 0.1, "scale": 2.0},
        "keywords": ["dog"],
    }


async def test_get_sticker_set_parses():
    bot, _ = fake_bot(
        {
            "name": "Pack",
            "title": "My Pack",
            "sticker_type": "regular",
            "stickers": [
                {"file_id": "s1", "file_unique_id": "u1", "type": "regular",
                 "width": 512, "height": 512}
            ],
            "thumbnail": {"file_id": "t1", "file_unique_id": "tu1", "width": 100, "height": 100},
        }
    )
    sset = await bot.get_sticker_set("Pack")
    assert isinstance(sset, StickerSet)
    assert sset.title == "My Pack" and len(sset.stickers) == 1
    assert sset.stickers[0].file_id == "s1"
    assert sset.thumbnail is not None and sset.thumbnail.file_id == "t1"


async def test_get_custom_emoji_stickers_params_and_parse():
    bot, session = fake_bot(
        [{"file_id": "e1", "file_unique_id": "u1", "type": "custom_emoji",
          "width": 100, "height": 100}]
    )
    stickers = await bot.get_custom_emoji_stickers(["123", "456"])
    assert stickers[0].file_id == "e1"
    assert session.calls == [
        ("getCustomEmojiStickers", {"custom_emoji_ids": ["123", "456"]})
    ]


async def test_create_new_sticker_set_serializes_input_stickers():
    bot, session = fake_bot(True)
    ok = await bot.create_new_sticker_set(
        1, "pack_by_bot", "Pack",
        [InputSticker("fid", format="static", emoji_list=["\N{CAT FACE}"])],
    )
    assert ok is True
    method, params = session.calls[0]
    assert method == "createNewStickerSet"
    assert params["stickers"] == [
        {"sticker": "fid", "format": "static", "emoji_list": ["\N{CAT FACE}"]}
    ]


async def test_add_sticker_to_set_serializes_single_input_sticker():
    bot, session = fake_bot(True)
    await bot.add_sticker_to_set(
        1, "pack", InputSticker("fid", format="static", emoji_list=["\N{CAT FACE}"])
    )
    _, params = session.calls[0]
    assert params["sticker"] == {
        "sticker": "fid", "format": "static", "emoji_list": ["\N{CAT FACE}"]
    }


async def test_set_sticker_mask_position_serializes():
    bot, session = fake_bot(True)
    await bot.set_sticker_mask_position(
        "fid", mask_position=MaskPosition("eyes", 0.0, 0.0, 1.0)
    )
    _, params = session.calls[0]
    assert params["mask_position"] == {
        "point": "eyes", "x_shift": 0.0, "y_shift": 0.0, "scale": 1.0
    }


async def test_sticker_set_simple_bool_methods():
    bot, session = fake_bot(True)
    assert await bot.delete_sticker_from_set("fid") is True
    assert session.calls[0] == ("deleteStickerFromSet", {"sticker": "fid"})
    assert await bot.set_sticker_set_title("pack", "New Title") is True
    assert session.calls[1] == ("setStickerSetTitle", {"name": "pack", "title": "New Title"})


async def test_upload_sticker_file_uploads_and_parses_file():
    captured: dict[str, Any] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["content_type"] = request.headers.get("content-type", "")
        captured["body"] = request.content
        return httpx.Response(
            200, json={"ok": True, "result": {"file_id": "F", "file_unique_id": "U"}}
        )

    bot = mock_bot(handler)
    try:
        f = await bot.upload_sticker_file(7, InputFile(b"WEBP", filename="s.webp"), "static")
        assert f.file_id == "F"
        assert captured["content_type"].startswith("multipart/form-data")
        assert b"s.webp" in captured["body"] and b"WEBP" in captured["body"]
        assert b'name="sticker_format"' in captured["body"] and b"static" in captured["body"]
    finally:
        await bot.session.close()
