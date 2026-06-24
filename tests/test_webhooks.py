"""Tests for webhook intake and the built-in server."""
from __future__ import annotations

import asyncio
import json

from moonlygram.ext import (
    Application,
    CommandHandler,
)
from conftest import (
    _MESSAGE_DICT,
    fake_bot,
)


async def test_set_webhook_builds_params():
    bot, session = fake_bot(True)
    ok = await bot.set_webhook("https://x/hook", secret_token="s", allowed_updates=["message"])
    assert ok is True
    assert session.calls == [
        ("setWebhook", {"url": "https://x/hook", "secret_token": "s", "allowed_updates": ["message"]})
    ]


async def test_get_webhook_info_parses():
    bot, _ = fake_bot(
        {"url": "https://x/hook", "has_custom_certificate": False, "pending_update_count": 3, "max_connections": 40}
    )
    info = await bot.get_webhook_info()
    assert info.url == "https://x/hook"
    assert info.pending_update_count == 3
    assert info.max_connections == 40


async def test_feed_webhook_update_dispatches():
    bot, _ = fake_bot()
    app = Application(bot)
    seen: list[int] = []

    async def go(update, context):
        seen.append(update.update_id)

    app.add_handler(CommandHandler("go", go))
    await app.feed_webhook_update({"update_id": 11, "message": dict(_MESSAGE_DICT, text="/go")})

    assert seen == [11]


async def test_webhook_server_dispatches_and_validates():
    bot, _ = fake_bot()
    app = Application(bot)
    seen: list[int] = []

    async def go(update, context):
        seen.append(update.update_id)

    app.add_handler(CommandHandler("go", go))
    task = asyncio.create_task(
        app.start_webhook(port=0, url_path="hook", secret_token="s3cret")
    )
    try:
        for _ in range(200):
            if app._webhook_server is not None:
                break
            await asyncio.sleep(0.01)
        assert app._webhook_server is not None
        port = app._webhook_server.sockets[0].getsockname()[1]

        async def post(path: str, body: bytes, secret: str | None = None) -> str:
            reader, writer = await asyncio.open_connection("127.0.0.1", port)
            head = f"POST /{path} HTTP/1.1\r\nHost: x\r\nContent-Length: {len(body)}\r\n"
            if secret is not None:
                head += f"X-Telegram-Bot-Api-Secret-Token: {secret}\r\n"
            head += "\r\n"
            writer.write(head.encode() + body)
            await writer.drain()
            status_line = await reader.readline()
            writer.close()
            return status_line.decode()

        body = json.dumps({"update_id": 3, "message": dict(_MESSAGE_DICT, text="/go")}).encode()
        assert "200" in await post("hook", body, secret="s3cret")
        assert "403" in await post("hook", body, secret="wrong")
        assert "404" in await post("nope", body, secret="s3cret")

        for _ in range(200):
            if seen:
                break
            await asyncio.sleep(0.01)
        assert seen == [3]
    finally:
        app.stop()
        await asyncio.wait_for(task, timeout=2)
