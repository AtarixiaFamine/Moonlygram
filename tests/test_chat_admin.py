"""Tests for chat administration and member management."""
from __future__ import annotations

from typing import Any

import httpx

from moonlygram import (
    BotCommand,
    ChatAdministratorRights,
    ChatPermissions,
    InputFile,
)
from moonlygram.ext import (
    Application,
    ChatJoinRequestHandler,
    ChatMemberHandler,
)
from moonlygram.types import Update
from conftest import (
    _msg,
    _update,
    fake_bot,
    mock_bot,
)


_MY_CHAT_MEMBER_RAW = {
    "update_id": 1,
    "my_chat_member": {
        "chat": {"id": 100, "type": "group"},
        "from": {"id": 5, "is_bot": False, "first_name": "A"},
        "date": 0,
        "old_chat_member": {"status": "member", "user": {"id": 7, "is_bot": True, "first_name": "Bot"}},
        "new_chat_member": {"status": "administrator", "user": {"id": 7, "is_bot": True, "first_name": "Bot"}},
    },
}

_CHAT_JOIN_REQUEST_RAW = {
    "update_id": 1,
    "chat_join_request": {
        "chat": {"id": 100, "type": "supergroup"},
        "from": {"id": 5, "is_bot": False, "first_name": "A"},
        "user_chat_id": 555,
        "date": 0,
    },
}


class TestChatAdministrationAndBotCommands:
    async def test_ban_chat_member_params(self):
        bot, session = fake_bot(True)
        assert await bot.ban_chat_member(10, 20, revoke_messages=True) is True
        assert session.calls == [
            ("banChatMember", {"chat_id": 10, "user_id": 20, "revoke_messages": True})
        ]

    async def test_restrict_chat_member_serializes_permissions(self):
        bot, session = fake_bot(True)
        perms = ChatPermissions(can_send_messages=True, can_send_polls=False)
        assert await bot.restrict_chat_member(1, 2, perms) is True
        method, params = session.calls[0]
        assert method == "restrictChatMember"
        assert params["permissions"] == {"can_send_messages": True, "can_send_polls": False}

    async def test_promote_chat_member_flags(self):
        bot, session = fake_bot(True)
        await bot.promote_chat_member(1, 2, can_delete_messages=True, can_pin_messages=True)
        _, params = session.calls[0]
        assert params == {"chat_id": 1, "user_id": 2, "can_delete_messages": True, "can_pin_messages": True}

    async def test_get_chat_member_and_admins(self):
        bot, _ = fake_bot({"status": "administrator", "user": {"id": 5, "is_bot": False, "first_name": "A"}})
        member = await bot.get_chat_member(1, 5)
        assert member.status == "administrator" and member.user.id == 5

        bot2, _ = fake_bot(
            [
                {"status": "creator", "user": {"id": 1, "is_bot": False, "first_name": "A"}},
                {"status": "administrator", "user": {"id": 2, "is_bot": False, "first_name": "B"}},
            ]
        )
        admins = await bot2.get_chat_administrators(1)
        assert [m.status for m in admins] == ["creator", "administrator"]

    async def test_get_chat_member_count(self):
        bot, _ = fake_bot(42)
        assert await bot.get_chat_member_count(1) == 42

    async def test_create_chat_invite_link_parses(self):
        bot, _ = fake_bot(
            {
                "invite_link": "https://t.me/+abc",
                "creator": {"id": 1, "is_bot": True, "first_name": "B"},
                "is_primary": False,
                "is_revoked": False,
                "member_limit": 10,
            }
        )
        link = await bot.create_chat_invite_link(1, member_limit=10)
        assert link.invite_link == "https://t.me/+abc" and link.member_limit == 10

    async def test_set_and_get_my_commands(self):
        bot, session = fake_bot([{"command": "start", "description": "Begin"}])
        await bot.set_my_commands([BotCommand("start", "Begin"), BotCommand("help", "Show help")])
        method, params = session.calls[0]
        assert method == "setMyCommands"
        assert params["commands"] == [
            {"command": "start", "description": "Begin"},
            {"command": "help", "description": "Show help"},
        ]
        assert await bot.get_my_commands() == [BotCommand("start", "Begin")]

    def test_update_parses_chat_member(self):
        update = Update.from_dict(_MY_CHAT_MEMBER_RAW)
        assert update.my_chat_member is not None
        assert update.my_chat_member.new_chat_member.status == "administrator"
        assert update.effective_chat_id == 100
        assert update.effective_user_id == 5

    async def test_chat_member_handler_dispatch(self):
        bot, _ = fake_bot()
        app = Application(bot)
        seen: list[str] = []

        async def on_member(update, context):
            seen.append(update.my_chat_member.new_chat_member.status)

        app.add_handler(ChatMemberHandler(on_member, kind=ChatMemberHandler.MY_CHAT_MEMBER))
        await app.process_update(Update.from_dict(_MY_CHAT_MEMBER_RAW))
        await app.process_update(_update(_msg("hi")))  # not a membership update: ignored

        assert seen == ["administrator"]


class TestChatAndMemberManagement:
    async def test_approve_chat_join_request_params(self):
        bot, session = fake_bot(True)
        assert await bot.approve_chat_join_request(10, 20) is True
        assert session.calls == [("approveChatJoinRequest", {"chat_id": 10, "user_id": 20})]

    async def test_ban_chat_sender_chat_params(self):
        bot, session = fake_bot(True)
        assert await bot.ban_chat_sender_chat(10, 99) is True
        assert session.calls == [("banChatSenderChat", {"chat_id": 10, "sender_chat_id": 99})]

    async def test_set_chat_administrator_custom_title_params(self):
        bot, session = fake_bot(True)
        await bot.set_chat_administrator_custom_title(1, 2, "Boss")
        assert session.calls == [
            ("setChatAdministratorCustomTitle", {"chat_id": 1, "user_id": 2, "custom_title": "Boss"})
        ]

    async def test_edit_chat_invite_link_parses(self):
        bot, session = fake_bot(
            {
                "invite_link": "https://t.me/+x",
                "creator": {"id": 1, "is_bot": True, "first_name": "B"},
                "is_primary": False,
                "is_revoked": False,
                "name": "VIP",
            }
        )
        link = await bot.edit_chat_invite_link(1, "https://t.me/+x", name="VIP")
        assert link.name == "VIP"
        assert session.calls == [
            ("editChatInviteLink", {"chat_id": 1, "invite_link": "https://t.me/+x", "name": "VIP"})
        ]

    async def test_set_chat_photo_uploads_inputfile(self):
        captured: dict[str, Any] = {}

        def handler(request: httpx.Request) -> httpx.Response:
            captured["content_type"] = request.headers.get("content-type", "")
            captured["body"] = request.content
            return httpx.Response(200, json={"ok": True, "result": True})

        bot = mock_bot(handler)
        try:
            assert await bot.set_chat_photo(5, InputFile(b"IMG", filename="pic.jpg")) is True
            assert captured["content_type"].startswith("multipart/form-data")
            assert b"pic.jpg" in captured["body"] and b"IMG" in captured["body"]
        finally:
            await bot.session.close()

    async def test_get_user_profile_photos_parses(self):
        bot, _ = fake_bot(
            {
                "total_count": 1,
                "photos": [[{"file_id": "p", "file_unique_id": "u", "width": 1, "height": 1}]],
            }
        )
        result = await bot.get_user_profile_photos(7)
        assert result.total_count == 1
        assert result.photos[0][0].file_id == "p"

    async def test_get_user_chat_boosts_parses(self):
        bot, _ = fake_bot(
            {
                "boosts": [
                    {
                        "boost_id": "b1",
                        "add_date": 100,
                        "expiration_date": 200,
                        "source": {
                            "source": "premium",
                            "user": {"id": 9, "is_bot": False, "first_name": "U"},
                        },
                    }
                ]
            }
        )
        boosts = await bot.get_user_chat_boosts(1, 9)
        assert len(boosts.boosts) == 1
        boost = boosts.boosts[0]
        assert boost.boost_id == "b1" and boost.source.source == "premium"
        assert boost.source.user is not None and boost.source.user.id == 9

    async def test_chat_menu_button_set_and_get(self):
        bot, session = fake_bot({"type": "default"})
        await bot.set_chat_menu_button(chat_id=1, menu_button={"type": "commands"})
        assert session.calls[0] == (
            "setChatMenuButton",
            {"chat_id": 1, "menu_button": {"type": "commands"}},
        )
        assert await bot.get_chat_menu_button(chat_id=1) == {"type": "default"}

    async def test_default_administrator_rights_round_trip(self):
        bot, session = fake_bot(True)
        rights = ChatAdministratorRights(
            is_anonymous=True, can_manage_chat=True, can_delete_messages=False
        )
        await bot.set_my_default_administrator_rights(rights=rights)
        _, params = session.calls[0]
        assert params["rights"] == {
            "is_anonymous": True,
            "can_manage_chat": True,
            "can_delete_messages": False,
        }

        bot2, _ = fake_bot(
            {"is_anonymous": False, "can_manage_chat": True, "can_delete_messages": True}
        )
        got = await bot2.get_my_default_administrator_rights()
        assert got.can_manage_chat is True and got.is_anonymous is False

    def test_update_parses_chat_join_request(self):
        update = Update.from_dict(_CHAT_JOIN_REQUEST_RAW)
        assert update.chat_join_request is not None
        assert update.chat_join_request.user_chat_id == 555
        assert update.effective_chat_id == 100
        assert update.effective_user_id == 5

    async def test_chat_join_request_handler_and_approve_shortcut(self):
        bot, session = fake_bot(True)
        app = Application(bot)
        seen: list[int] = []

        async def on_request(update, context):
            seen.append(update.chat_join_request.from_user.id)
            await update.chat_join_request.approve()

        app.add_handler(ChatJoinRequestHandler(on_request))
        await app.process_update(Update.from_dict(_CHAT_JOIN_REQUEST_RAW))
        await app.process_update(_update(_msg("hi")))  # not a join request: ignored

        assert seen == [5]
        assert session.calls == [("approveChatJoinRequest", {"chat_id": 100, "user_id": 5})]
