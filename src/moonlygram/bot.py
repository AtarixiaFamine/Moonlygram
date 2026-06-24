"""The Bot class.

Bot owns a Session and exposes Telegram Bot API methods as async functions.
It holds no handler or polling logic; the Application layer in moonlygram.ext
drives it.
"""
from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, Any, Optional, Protocol, cast

from .defaults import Defaults
from .session import Session
from .types import (
    BotCommand,
    BotDescription,
    BotName,
    BotShortDescription,
    Chat,
    ChatAdministratorRights,
    ChatInviteLink,
    ChatMember,
    ChatPermissions,
    File,
    FileInput,
    ForumTopic,
    InlineQueryResult,
    InputMedia,
    InputSticker,
    MaskPosition,
    Message,
    MessageId,
    Poll,
    ReactionType,
    ReplyMarkup,
    SentWebAppMessage,
    Sticker,
    StickerSet,
    User,
    UserChatBoosts,
    UserProfilePhotos,
    WebhookInfo,
)

if TYPE_CHECKING:
    from .rich import RichMessage

_DEFAULTABLE = ("parse_mode", "disable_notification", "protect_content")


class RateLimiter(Protocol):
    """The rate-limiter contract Bot depends on.

    Bot stays decoupled from moonlygram.ext: any object with these methods works
    (the built-in implementation is ext.AIORateLimiter). Defined structurally so
    core never imports ext.
    """

    async def initialize(self) -> None: ...

    async def shutdown(self) -> None: ...

    async def process_request(
        self,
        callback: Callable[[], Awaitable[Any]],
        *,
        chat_id: Optional[Any] = None,
    ) -> Any: ...


class CallbackDataCache(Protocol):
    """The arbitrary-callback-data cache contract Bot depends on.

    Satisfied by ext.CallbackDataCache; defined structurally so core never
    imports ext.
    """

    def process_keyboard(self, markup: Any) -> Any: ...

    def process_callback_query(self, query: Any) -> None: ...


class Bot:
    def __init__(
        self,
        token: str,
        *,
        defaults: Optional[Defaults] = None,
        rate_limiter: Optional[RateLimiter] = None,
        callback_data_cache: Optional[CallbackDataCache] = None,
        **session_kwargs: Any,
    ) -> None:
        self.session = Session(token, **session_kwargs)
        self.defaults = defaults
        self.rate_limiter = rate_limiter
        self.callback_data_cache = callback_data_cache

    async def __aenter__(self) -> "Bot":
        return self

    async def __aexit__(self, *exc: object) -> None:
        await self.session.close()

    async def close(self) -> None:
        """Close the underlying HTTP session."""
        await self.session.close()

    async def call(self, method: str, /, **params: Any) -> Any:
        """Call any Bot API method directly.

        An escape hatch for methods or parameters Moonlygram does not yet model.
        """
        return await self._call(method, **params)

    async def _call(self, method: str, /, **params: Any) -> Any:
        if self.defaults is not None:
            for key in _DEFAULTABLE:
                if key in params and params[key] is None:
                    params[key] = getattr(self.defaults, key)
        if self.callback_data_cache is not None and params.get("reply_markup") is not None:
            params["reply_markup"] = self.callback_data_cache.process_keyboard(
                params["reply_markup"]
            )
        if self.rate_limiter is not None:
            return await self.rate_limiter.process_request(
                lambda: self.session.call(method, **params),
                chat_id=params.get("chat_id"),
            )
        return await self.session.call(method, **params)

    async def get_me(self) -> User:
        """Return the bot's own user account."""
        return User.from_dict(await self._call("getMe"))

    async def send_message(
        self,
        chat_id: int | str,
        text: str,
        *,
        parse_mode: Optional[str] = None,
        reply_to_message_id: Optional[int] = None,
        reply_markup: Optional[ReplyMarkup] = None,
    ) -> Message:
        """Send a text message to a chat."""
        return Message.from_dict(
            await self._call(
                "sendMessage",
                chat_id=chat_id,
                text=text,
                parse_mode=parse_mode,
                reply_to_message_id=reply_to_message_id,
                reply_markup=reply_markup,
            )
        )

    @staticmethod
    def _rich_message(html: Any, markdown: Optional[str]) -> dict[str, Any]:
        """Build the rich_message payload, accepting a RichMessage for html."""
        if html is not None and hasattr(html, "to_html"):
            html = html.to_html()
        if (html is None) == (markdown is None):
            raise ValueError("Pass exactly one of `html` or `markdown`.")
        return {"html": html} if html is not None else {"markdown": markdown}

    async def send_rich_message(
        self,
        chat_id: int | str,
        *,
        html: "Optional[str | RichMessage]" = None,
        markdown: Optional[str] = None,
    ) -> Message:
        """Send a Bot API 10.1 rich message.

        Pass exactly one of html or markdown. html may be a rich-message HTML
        string or a RichMessage builder; markdown is rendered by Telegram.
        """
        return Message.from_dict(
            await self._call(
                "sendRichMessage",
                chat_id=chat_id,
                rich_message=self._rich_message(html, markdown),
            )
        )

    async def send_rich_message_draft(
        self,
        chat_id: int | str,
        draft_id: int,
        *,
        html: "Optional[str | RichMessage]" = None,
        markdown: Optional[str] = None,
    ) -> bool:
        """Send an ephemeral rich-message draft (about a 30s TTL).

        Use this to stream a response by repeatedly updating the same draft_id;
        send the final version with send_rich_message. Pass exactly one of html
        or markdown.
        """
        return bool(
            await self._call(
                "sendRichMessageDraft",
                chat_id=chat_id,
                draft_id=draft_id,
                rich_message=self._rich_message(html, markdown),
            )
        )

    async def send_photo(
        self,
        chat_id: int | str,
        photo: FileInput,
        *,
        caption: Optional[str] = None,
        parse_mode: Optional[str] = None,
        reply_markup: Optional[ReplyMarkup] = None,
        reply_to_message_id: Optional[int] = None,
    ) -> Message:
        """Send a photo. Pass an InputFile to upload, or a file_id / URL string."""
        return Message.from_dict(
            await self._call(
                "sendPhoto",
                chat_id=chat_id,
                photo=photo,
                caption=caption,
                parse_mode=parse_mode,
                reply_markup=reply_markup,
                reply_to_message_id=reply_to_message_id,
            )
        )

    async def send_document(
        self,
        chat_id: int | str,
        document: FileInput,
        *,
        caption: Optional[str] = None,
        parse_mode: Optional[str] = None,
        reply_markup: Optional[ReplyMarkup] = None,
        reply_to_message_id: Optional[int] = None,
    ) -> Message:
        """Send a general file. Pass an InputFile to upload, or a file_id / URL."""
        return Message.from_dict(
            await self._call(
                "sendDocument",
                chat_id=chat_id,
                document=document,
                caption=caption,
                parse_mode=parse_mode,
                reply_markup=reply_markup,
                reply_to_message_id=reply_to_message_id,
            )
        )

    async def send_audio(
        self,
        chat_id: int | str,
        audio: FileInput,
        *,
        caption: Optional[str] = None,
        parse_mode: Optional[str] = None,
        reply_markup: Optional[ReplyMarkup] = None,
        reply_to_message_id: Optional[int] = None,
    ) -> Message:
        """Send an audio file shown in the music player."""
        return Message.from_dict(
            await self._call(
                "sendAudio",
                chat_id=chat_id,
                audio=audio,
                caption=caption,
                parse_mode=parse_mode,
                reply_markup=reply_markup,
                reply_to_message_id=reply_to_message_id,
            )
        )

    async def send_video(
        self,
        chat_id: int | str,
        video: FileInput,
        *,
        caption: Optional[str] = None,
        parse_mode: Optional[str] = None,
        reply_markup: Optional[ReplyMarkup] = None,
        reply_to_message_id: Optional[int] = None,
    ) -> Message:
        """Send a video file."""
        return Message.from_dict(
            await self._call(
                "sendVideo",
                chat_id=chat_id,
                video=video,
                caption=caption,
                parse_mode=parse_mode,
                reply_markup=reply_markup,
                reply_to_message_id=reply_to_message_id,
            )
        )

    async def send_animation(
        self,
        chat_id: int | str,
        animation: FileInput,
        *,
        caption: Optional[str] = None,
        parse_mode: Optional[str] = None,
        reply_markup: Optional[ReplyMarkup] = None,
        reply_to_message_id: Optional[int] = None,
    ) -> Message:
        """Send an animation (GIF or soundless H.264/MPEG-4)."""
        return Message.from_dict(
            await self._call(
                "sendAnimation",
                chat_id=chat_id,
                animation=animation,
                caption=caption,
                parse_mode=parse_mode,
                reply_markup=reply_markup,
                reply_to_message_id=reply_to_message_id,
            )
        )

    async def send_voice(
        self,
        chat_id: int | str,
        voice: FileInput,
        *,
        caption: Optional[str] = None,
        parse_mode: Optional[str] = None,
        reply_markup: Optional[ReplyMarkup] = None,
        reply_to_message_id: Optional[int] = None,
    ) -> Message:
        """Send a voice note."""
        return Message.from_dict(
            await self._call(
                "sendVoice",
                chat_id=chat_id,
                voice=voice,
                caption=caption,
                parse_mode=parse_mode,
                reply_markup=reply_markup,
                reply_to_message_id=reply_to_message_id,
            )
        )

    async def send_video_note(
        self,
        chat_id: int | str,
        video_note: FileInput,
        *,
        reply_markup: Optional[ReplyMarkup] = None,
        reply_to_message_id: Optional[int] = None,
    ) -> Message:
        """Send a rounded square video note."""
        return Message.from_dict(
            await self._call(
                "sendVideoNote",
                chat_id=chat_id,
                video_note=video_note,
                reply_markup=reply_markup,
                reply_to_message_id=reply_to_message_id,
            )
        )

    async def send_sticker(
        self,
        chat_id: int | str,
        sticker: FileInput,
        *,
        reply_markup: Optional[ReplyMarkup] = None,
        reply_to_message_id: Optional[int] = None,
    ) -> Message:
        """Send a sticker."""
        return Message.from_dict(
            await self._call(
                "sendSticker",
                chat_id=chat_id,
                sticker=sticker,
                reply_markup=reply_markup,
                reply_to_message_id=reply_to_message_id,
            )
        )

    async def send_location(
        self,
        chat_id: int | str,
        latitude: float,
        longitude: float,
        *,
        horizontal_accuracy: Optional[float] = None,
        reply_markup: Optional[ReplyMarkup] = None,
        reply_to_message_id: Optional[int] = None,
    ) -> Message:
        """Send a point on the map."""
        return Message.from_dict(
            await self._call(
                "sendLocation",
                chat_id=chat_id,
                latitude=latitude,
                longitude=longitude,
                horizontal_accuracy=horizontal_accuracy,
                reply_markup=reply_markup,
                reply_to_message_id=reply_to_message_id,
            )
        )

    async def send_contact(
        self,
        chat_id: int | str,
        phone_number: str,
        first_name: str,
        *,
        last_name: Optional[str] = None,
        reply_markup: Optional[ReplyMarkup] = None,
        reply_to_message_id: Optional[int] = None,
    ) -> Message:
        """Send a phone contact."""
        return Message.from_dict(
            await self._call(
                "sendContact",
                chat_id=chat_id,
                phone_number=phone_number,
                first_name=first_name,
                last_name=last_name,
                reply_markup=reply_markup,
                reply_to_message_id=reply_to_message_id,
            )
        )

    async def send_poll(
        self,
        chat_id: int | str,
        question: str,
        options: list[str],
        *,
        is_anonymous: Optional[bool] = None,
        type: Optional[str] = None,
        allows_multiple_answers: Optional[bool] = None,
        reply_markup: Optional[ReplyMarkup] = None,
        reply_to_message_id: Optional[int] = None,
    ) -> Message:
        """Send a native poll."""
        return Message.from_dict(
            await self._call(
                "sendPoll",
                chat_id=chat_id,
                question=question,
                options=options,
                is_anonymous=is_anonymous,
                type=type,
                allows_multiple_answers=allows_multiple_answers,
                reply_markup=reply_markup,
                reply_to_message_id=reply_to_message_id,
            )
        )

    async def send_dice(
        self,
        chat_id: int | str,
        *,
        emoji: Optional[str] = None,
        reply_markup: Optional[ReplyMarkup] = None,
        reply_to_message_id: Optional[int] = None,
    ) -> Message:
        """Send an animated dice (or other emoji) with a random value."""
        return Message.from_dict(
            await self._call(
                "sendDice",
                chat_id=chat_id,
                emoji=emoji,
                reply_markup=reply_markup,
                reply_to_message_id=reply_to_message_id,
            )
        )

    async def stop_poll(
        self,
        chat_id: int | str,
        message_id: int,
        *,
        reply_markup: Optional[ReplyMarkup] = None,
    ) -> Poll:
        """Stop an active poll and return its final state."""
        return Poll.from_dict(
            await self._call(
                "stopPoll",
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=reply_markup,
            )
        )

    async def send_venue(
        self,
        chat_id: int | str,
        latitude: float,
        longitude: float,
        title: str,
        address: str,
        *,
        reply_markup: Optional[ReplyMarkup] = None,
        reply_to_message_id: Optional[int] = None,
    ) -> Message:
        """Send information about a venue."""
        return Message.from_dict(
            await self._call(
                "sendVenue",
                chat_id=chat_id,
                latitude=latitude,
                longitude=longitude,
                title=title,
                address=address,
                reply_markup=reply_markup,
                reply_to_message_id=reply_to_message_id,
            )
        )

    async def send_media_group(
        self,
        chat_id: int | str,
        media: list[InputMedia],
        *,
        disable_notification: Optional[bool] = None,
        reply_to_message_id: Optional[int] = None,
    ) -> list[Message]:
        """Send a group of photos, videos, documents, or audios as an album."""
        result = await self._call(
            "sendMediaGroup",
            chat_id=chat_id,
            media=[m.to_dict() if hasattr(m, "to_dict") else m for m in media],
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
        )
        return [Message.from_dict(m) for m in result]

    async def edit_message_media(
        self,
        media: InputMedia,
        *,
        chat_id: Optional[int | str] = None,
        message_id: Optional[int] = None,
        inline_message_id: Optional[str] = None,
        reply_markup: Optional[ReplyMarkup] = None,
    ) -> Message | bool:
        """Replace the media of a message; True for inline messages."""
        return _edited(
            await self._call(
                "editMessageMedia",
                media=media,
                chat_id=chat_id,
                message_id=message_id,
                inline_message_id=inline_message_id,
                reply_markup=reply_markup,
            )
        )

    async def edit_message_live_location(
        self,
        latitude: float,
        longitude: float,
        *,
        chat_id: Optional[int | str] = None,
        message_id: Optional[int] = None,
        inline_message_id: Optional[str] = None,
        reply_markup: Optional[ReplyMarkup] = None,
    ) -> Message | bool:
        """Update a live location message; True for inline messages."""
        return _edited(
            await self._call(
                "editMessageLiveLocation",
                latitude=latitude,
                longitude=longitude,
                chat_id=chat_id,
                message_id=message_id,
                inline_message_id=inline_message_id,
                reply_markup=reply_markup,
            )
        )

    async def stop_message_live_location(
        self,
        *,
        chat_id: Optional[int | str] = None,
        message_id: Optional[int] = None,
        inline_message_id: Optional[str] = None,
        reply_markup: Optional[ReplyMarkup] = None,
    ) -> Message | bool:
        """Stop updating a live location message; True for inline messages."""
        return _edited(
            await self._call(
                "stopMessageLiveLocation",
                chat_id=chat_id,
                message_id=message_id,
                inline_message_id=inline_message_id,
                reply_markup=reply_markup,
            )
        )

    async def forward_messages(
        self,
        chat_id: int | str,
        from_chat_id: int | str,
        message_ids: list[int],
        *,
        disable_notification: Optional[bool] = None,
    ) -> list[MessageId]:
        """Forward several messages at once."""
        result = await self._call(
            "forwardMessages",
            chat_id=chat_id,
            from_chat_id=from_chat_id,
            message_ids=message_ids,
            disable_notification=disable_notification,
        )
        return [MessageId.from_dict(m) for m in result]

    async def copy_messages(
        self,
        chat_id: int | str,
        from_chat_id: int | str,
        message_ids: list[int],
        *,
        disable_notification: Optional[bool] = None,
        remove_caption: Optional[bool] = None,
    ) -> list[MessageId]:
        """Copy several messages at once without a forward header."""
        result = await self._call(
            "copyMessages",
            chat_id=chat_id,
            from_chat_id=from_chat_id,
            message_ids=message_ids,
            disable_notification=disable_notification,
            remove_caption=remove_caption,
        )
        return [MessageId.from_dict(m) for m in result]

    async def delete_messages(self, chat_id: int | str, message_ids: list[int]) -> bool:
        """Delete several messages at once."""
        return bool(
            await self._call(
                "deleteMessages", chat_id=chat_id, message_ids=message_ids
            )
        )

    async def set_message_reaction(
        self,
        chat_id: int | str,
        message_id: int,
        *,
        reaction: Optional[list[ReactionType]] = None,
        is_big: Optional[bool] = None,
    ) -> bool:
        """Set the bot's reaction(s) on a message; pass no reaction to clear."""
        return bool(
            await self._call(
                "setMessageReaction",
                chat_id=chat_id,
                message_id=message_id,
                reaction=(
                    [r.to_dict() if hasattr(r, "to_dict") else r for r in reaction]
                    if reaction is not None
                    else None
                ),
                is_big=is_big,
            )
        )

    async def get_file(self, file_id: str) -> File:
        """Fetch metadata for a file, including a file_path for downloading."""
        return File.from_dict(await self._call("getFile", file_id=file_id))

    async def download_file(self, file_path: str) -> bytes:
        """Download a file's bytes given a file_path from get_file."""
        return await self.session.download(file_path)

    async def set_webhook(
        self,
        url: str,
        *,
        secret_token: Optional[str] = None,
        allowed_updates: Optional[list[str]] = None,
        drop_pending_updates: Optional[bool] = None,
        max_connections: Optional[int] = None,
    ) -> bool:
        """Register a webhook URL for Telegram to deliver updates to."""
        return bool(
            await self._call(
                "setWebhook",
                url=url,
                secret_token=secret_token,
                allowed_updates=allowed_updates,
                drop_pending_updates=drop_pending_updates,
                max_connections=max_connections,
            )
        )

    async def delete_webhook(self, *, drop_pending_updates: Optional[bool] = None) -> bool:
        """Remove the webhook and return to long polling."""
        return bool(
            await self._call(
                "deleteWebhook", drop_pending_updates=drop_pending_updates
            )
        )

    async def get_webhook_info(self) -> WebhookInfo:
        """Return the current webhook status."""
        return WebhookInfo.from_dict(await self._call("getWebhookInfo"))

    async def forward_message(
        self,
        chat_id: int | str,
        from_chat_id: int | str,
        message_id: int,
        *,
        disable_notification: Optional[bool] = None,
    ) -> Message:
        """Forward a message from one chat to another."""
        return Message.from_dict(
            await self._call(
                "forwardMessage",
                chat_id=chat_id,
                from_chat_id=from_chat_id,
                message_id=message_id,
                disable_notification=disable_notification,
            )
        )

    async def copy_message(
        self,
        chat_id: int | str,
        from_chat_id: int | str,
        message_id: int,
        *,
        caption: Optional[str] = None,
        parse_mode: Optional[str] = None,
        reply_markup: Optional[ReplyMarkup] = None,
    ) -> MessageId:
        """Copy a message without a forward header, returning the new id."""
        return MessageId.from_dict(
            await self._call(
                "copyMessage",
                chat_id=chat_id,
                from_chat_id=from_chat_id,
                message_id=message_id,
                caption=caption,
                parse_mode=parse_mode,
                reply_markup=reply_markup,
            )
        )

    async def edit_message_text(
        self,
        text: str,
        *,
        chat_id: Optional[int | str] = None,
        message_id: Optional[int] = None,
        inline_message_id: Optional[str] = None,
        parse_mode: Optional[str] = None,
        reply_markup: Optional[ReplyMarkup] = None,
    ) -> Message | bool:
        """Edit the text of a message; returns True for inline messages."""
        return _edited(
            await self._call(
                "editMessageText",
                text=text,
                chat_id=chat_id,
                message_id=message_id,
                inline_message_id=inline_message_id,
                parse_mode=parse_mode,
                reply_markup=reply_markup,
            )
        )

    async def edit_message_caption(
        self,
        *,
        caption: Optional[str] = None,
        chat_id: Optional[int | str] = None,
        message_id: Optional[int] = None,
        inline_message_id: Optional[str] = None,
        parse_mode: Optional[str] = None,
        reply_markup: Optional[ReplyMarkup] = None,
    ) -> Message | bool:
        """Edit a message's caption; returns True for inline messages."""
        return _edited(
            await self._call(
                "editMessageCaption",
                caption=caption,
                chat_id=chat_id,
                message_id=message_id,
                inline_message_id=inline_message_id,
                parse_mode=parse_mode,
                reply_markup=reply_markup,
            )
        )

    async def edit_message_reply_markup(
        self,
        *,
        chat_id: Optional[int | str] = None,
        message_id: Optional[int] = None,
        inline_message_id: Optional[str] = None,
        reply_markup: Optional[ReplyMarkup] = None,
    ) -> Message | bool:
        """Edit only a message's inline keyboard; True for inline messages."""
        return _edited(
            await self._call(
                "editMessageReplyMarkup",
                chat_id=chat_id,
                message_id=message_id,
                inline_message_id=inline_message_id,
                reply_markup=reply_markup,
            )
        )

    async def delete_message(self, chat_id: int | str, message_id: int) -> bool:
        """Delete a message."""
        return bool(
            await self._call(
                "deleteMessage", chat_id=chat_id, message_id=message_id
            )
        )

    async def pin_chat_message(
        self,
        chat_id: int | str,
        message_id: int,
        *,
        disable_notification: Optional[bool] = None,
    ) -> bool:
        """Pin a message in a chat."""
        return bool(
            await self._call(
                "pinChatMessage",
                chat_id=chat_id,
                message_id=message_id,
                disable_notification=disable_notification,
            )
        )

    async def unpin_chat_message(
        self,
        chat_id: int | str,
        *,
        message_id: Optional[int] = None,
    ) -> bool:
        """Unpin a message, or the most recent pinned one if id is omitted."""
        return bool(
            await self._call(
                "unpinChatMessage", chat_id=chat_id, message_id=message_id
            )
        )

    async def unpin_all_chat_messages(self, chat_id: int | str) -> bool:
        """Unpin every pinned message in a chat."""
        return bool(
            await self._call("unpinAllChatMessages", chat_id=chat_id)
        )

    async def send_chat_action(self, chat_id: int | str, action: str) -> bool:
        """Show a status such as "typing" or "upload_photo" in a chat."""
        return bool(
            await self._call(
                "sendChatAction", chat_id=chat_id, action=action
            )
        )

    async def answer_callback_query(
        self,
        callback_query_id: str,
        *,
        text: Optional[str] = None,
        show_alert: Optional[bool] = None,
        url: Optional[str] = None,
        cache_time: Optional[int] = None,
    ) -> bool:
        """Acknowledge a callback query, optionally showing a toast or alert."""
        return bool(
            await self._call(
                "answerCallbackQuery",
                callback_query_id=callback_query_id,
                text=text,
                show_alert=show_alert,
                url=url,
                cache_time=cache_time,
            )
        )

    async def ban_chat_member(
        self,
        chat_id: int | str,
        user_id: int,
        *,
        until_date: Optional[int] = None,
        revoke_messages: Optional[bool] = None,
    ) -> bool:
        """Ban a user from a chat."""
        return bool(
            await self._call(
                "banChatMember",
                chat_id=chat_id,
                user_id=user_id,
                until_date=until_date,
                revoke_messages=revoke_messages,
            )
        )

    async def unban_chat_member(
        self,
        chat_id: int | str,
        user_id: int,
        *,
        only_if_banned: Optional[bool] = None,
    ) -> bool:
        """Unban a previously banned user."""
        return bool(
            await self._call(
                "unbanChatMember",
                chat_id=chat_id,
                user_id=user_id,
                only_if_banned=only_if_banned,
            )
        )

    async def restrict_chat_member(
        self,
        chat_id: int | str,
        user_id: int,
        permissions: ChatPermissions,
        *,
        until_date: Optional[int] = None,
    ) -> bool:
        """Restrict what a member may do in a supergroup."""
        return bool(
            await self._call(
                "restrictChatMember",
                chat_id=chat_id,
                user_id=user_id,
                permissions=permissions,
                until_date=until_date,
            )
        )

    async def promote_chat_member(
        self,
        chat_id: int | str,
        user_id: int,
        *,
        can_manage_chat: Optional[bool] = None,
        can_delete_messages: Optional[bool] = None,
        can_restrict_members: Optional[bool] = None,
        can_promote_members: Optional[bool] = None,
        can_change_info: Optional[bool] = None,
        can_invite_users: Optional[bool] = None,
        can_pin_messages: Optional[bool] = None,
        can_manage_topics: Optional[bool] = None,
    ) -> bool:
        """Promote or demote a member by toggling administrator rights."""
        return bool(
            await self._call(
                "promoteChatMember",
                chat_id=chat_id,
                user_id=user_id,
                can_manage_chat=can_manage_chat,
                can_delete_messages=can_delete_messages,
                can_restrict_members=can_restrict_members,
                can_promote_members=can_promote_members,
                can_change_info=can_change_info,
                can_invite_users=can_invite_users,
                can_pin_messages=can_pin_messages,
                can_manage_topics=can_manage_topics,
            )
        )

    async def set_chat_title(self, chat_id: int | str, title: str) -> bool:
        """Change a chat's title."""
        return bool(await self._call("setChatTitle", chat_id=chat_id, title=title))

    async def set_chat_description(
        self, chat_id: int | str, description: Optional[str] = None
    ) -> bool:
        """Change a chat's description."""
        return bool(
            await self._call(
                "setChatDescription", chat_id=chat_id, description=description
            )
        )

    async def set_chat_permissions(
        self, chat_id: int | str, permissions: ChatPermissions
    ) -> bool:
        """Set the default permissions for all members of a supergroup."""
        return bool(
            await self._call(
                "setChatPermissions", chat_id=chat_id, permissions=permissions
            )
        )

    async def get_chat(self, chat_id: int | str) -> Chat:
        """Fetch up-to-date information about a chat."""
        return Chat.from_dict(await self._call("getChat", chat_id=chat_id))

    async def get_chat_member(self, chat_id: int | str, user_id: int) -> ChatMember:
        """Fetch one member of a chat."""
        return ChatMember.from_dict(
            await self._call("getChatMember", chat_id=chat_id, user_id=user_id)
        )

    async def get_chat_administrators(self, chat_id: int | str) -> list[ChatMember]:
        """List the administrators of a chat."""
        result = await self._call("getChatAdministrators", chat_id=chat_id)
        return [ChatMember.from_dict(member) for member in result]

    async def get_chat_member_count(self, chat_id: int | str) -> int:
        """Return the number of members in a chat."""
        return int(await self._call("getChatMemberCount", chat_id=chat_id))

    async def leave_chat(self, chat_id: int | str) -> bool:
        """Leave a group, supergroup, or channel."""
        return bool(await self._call("leaveChat", chat_id=chat_id))

    async def export_chat_invite_link(self, chat_id: int | str) -> str:
        """Generate a new primary invite link, revoking the previous one."""
        return str(await self._call("exportChatInviteLink", chat_id=chat_id))

    async def create_chat_invite_link(
        self,
        chat_id: int | str,
        *,
        name: Optional[str] = None,
        expire_date: Optional[int] = None,
        member_limit: Optional[int] = None,
    ) -> ChatInviteLink:
        """Create an additional invite link for a chat."""
        return ChatInviteLink.from_dict(
            await self._call(
                "createChatInviteLink",
                chat_id=chat_id,
                name=name,
                expire_date=expire_date,
                member_limit=member_limit,
            )
        )

    async def edit_chat_invite_link(
        self,
        chat_id: int | str,
        invite_link: str,
        *,
        name: Optional[str] = None,
        expire_date: Optional[int] = None,
        member_limit: Optional[int] = None,
        creates_join_request: Optional[bool] = None,
    ) -> ChatInviteLink:
        """Edit a non-primary invite link created by the bot."""
        return ChatInviteLink.from_dict(
            await self._call(
                "editChatInviteLink",
                chat_id=chat_id,
                invite_link=invite_link,
                name=name,
                expire_date=expire_date,
                member_limit=member_limit,
                creates_join_request=creates_join_request,
            )
        )

    async def revoke_chat_invite_link(
        self, chat_id: int | str, invite_link: str
    ) -> ChatInviteLink:
        """Revoke an invite link created by the bot."""
        return ChatInviteLink.from_dict(
            await self._call(
                "revokeChatInviteLink", chat_id=chat_id, invite_link=invite_link
            )
        )

    async def approve_chat_join_request(self, chat_id: int | str, user_id: int) -> bool:
        """Approve a request to join a chat."""
        return bool(
            await self._call(
                "approveChatJoinRequest", chat_id=chat_id, user_id=user_id
            )
        )

    async def decline_chat_join_request(self, chat_id: int | str, user_id: int) -> bool:
        """Decline a request to join a chat."""
        return bool(
            await self._call(
                "declineChatJoinRequest", chat_id=chat_id, user_id=user_id
            )
        )

    async def set_chat_photo(self, chat_id: int | str, photo: FileInput) -> bool:
        """Set a chat's photo. Pass an InputFile to upload the new photo."""
        return bool(await self._call("setChatPhoto", chat_id=chat_id, photo=photo))

    async def delete_chat_photo(self, chat_id: int | str) -> bool:
        """Delete a chat's photo."""
        return bool(await self._call("deleteChatPhoto", chat_id=chat_id))

    async def set_chat_sticker_set(
        self, chat_id: int | str, sticker_set_name: str
    ) -> bool:
        """Set the group sticker set for a supergroup."""
        return bool(
            await self._call(
                "setChatStickerSet",
                chat_id=chat_id,
                sticker_set_name=sticker_set_name,
            )
        )

    async def delete_chat_sticker_set(self, chat_id: int | str) -> bool:
        """Delete the group sticker set from a supergroup."""
        return bool(await self._call("deleteChatStickerSet", chat_id=chat_id))

    async def ban_chat_sender_chat(
        self, chat_id: int | str, sender_chat_id: int
    ) -> bool:
        """Ban a channel from posting on its own behalf in a chat."""
        return bool(
            await self._call(
                "banChatSenderChat", chat_id=chat_id, sender_chat_id=sender_chat_id
            )
        )

    async def unban_chat_sender_chat(
        self, chat_id: int | str, sender_chat_id: int
    ) -> bool:
        """Unban a previously banned channel in a chat."""
        return bool(
            await self._call(
                "unbanChatSenderChat", chat_id=chat_id, sender_chat_id=sender_chat_id
            )
        )

    async def set_chat_administrator_custom_title(
        self, chat_id: int | str, user_id: int, custom_title: str
    ) -> bool:
        """Set a custom title for an administrator promoted by the bot."""
        return bool(
            await self._call(
                "setChatAdministratorCustomTitle",
                chat_id=chat_id,
                user_id=user_id,
                custom_title=custom_title,
            )
        )

    async def get_user_profile_photos(
        self,
        user_id: int,
        *,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> UserProfilePhotos:
        """Fetch a user's profile photos."""
        return UserProfilePhotos.from_dict(
            await self._call(
                "getUserProfilePhotos",
                user_id=user_id,
                offset=offset,
                limit=limit,
            )
        )

    async def get_user_chat_boosts(
        self, chat_id: int | str, user_id: int
    ) -> UserChatBoosts:
        """Fetch the boosts a user has added to a chat."""
        return UserChatBoosts.from_dict(
            await self._call(
                "getUserChatBoosts", chat_id=chat_id, user_id=user_id
            )
        )

    async def set_chat_menu_button(
        self,
        *,
        chat_id: Optional[int] = None,
        menu_button: Optional[dict[str, Any]] = None,
    ) -> bool:
        """Set the bot's menu button, for one chat or (with no chat) globally."""
        return bool(
            await self._call(
                "setChatMenuButton", chat_id=chat_id, menu_button=menu_button
            )
        )

    async def get_chat_menu_button(
        self, *, chat_id: Optional[int] = None
    ) -> dict[str, Any]:
        """Get the bot's menu button as a raw MenuButton dict."""
        return cast(
            "dict[str, Any]",
            await self._call("getChatMenuButton", chat_id=chat_id),
        )

    async def set_my_default_administrator_rights(
        self,
        *,
        rights: Optional[ChatAdministratorRights] = None,
        for_channels: Optional[bool] = None,
    ) -> bool:
        """Set the bot's default administrator rights for new groups or channels."""
        return bool(
            await self._call(
                "setMyDefaultAdministratorRights",
                rights=rights,
                for_channels=for_channels,
            )
        )

    async def get_my_default_administrator_rights(
        self, *, for_channels: Optional[bool] = None
    ) -> ChatAdministratorRights:
        """Get the bot's default administrator rights for new groups or channels."""
        return ChatAdministratorRights.from_dict(
            await self._call(
                "getMyDefaultAdministratorRights", for_channels=for_channels
            )
        )

    async def set_my_commands(
        self,
        commands: list[BotCommand],
        *,
        scope: Optional[dict[str, Any]] = None,
        language_code: Optional[str] = None,
    ) -> bool:
        """Set the bot's command menu."""
        return bool(
            await self._call(
                "setMyCommands",
                commands=[command.to_dict() for command in commands],
                scope=scope,
                language_code=language_code,
            )
        )

    async def get_my_commands(
        self,
        *,
        scope: Optional[dict[str, Any]] = None,
        language_code: Optional[str] = None,
    ) -> list[BotCommand]:
        """Get the bot's current command menu."""
        result = await self._call(
            "getMyCommands", scope=scope, language_code=language_code
        )
        return [BotCommand.from_dict(command) for command in result]

    async def delete_my_commands(
        self,
        *,
        scope: Optional[dict[str, Any]] = None,
        language_code: Optional[str] = None,
    ) -> bool:
        """Delete the bot's command menu for the given scope and language."""
        return bool(
            await self._call(
                "deleteMyCommands", scope=scope, language_code=language_code
            )
        )

    async def set_my_name(
        self,
        *,
        name: Optional[str] = None,
        language_code: Optional[str] = None,
    ) -> bool:
        """Set the bot's name, optionally for a specific language."""
        return bool(
            await self._call("setMyName", name=name, language_code=language_code)
        )

    async def get_my_name(self, *, language_code: Optional[str] = None) -> BotName:
        """Get the bot's name for the given language."""
        return BotName.from_dict(
            await self._call("getMyName", language_code=language_code)
        )

    async def set_my_description(
        self,
        *,
        description: Optional[str] = None,
        language_code: Optional[str] = None,
    ) -> bool:
        """Set the bot's description, shown in an empty chat with the bot."""
        return bool(
            await self._call(
                "setMyDescription",
                description=description,
                language_code=language_code,
            )
        )

    async def get_my_description(
        self, *, language_code: Optional[str] = None
    ) -> BotDescription:
        """Get the bot's description for the given language."""
        return BotDescription.from_dict(
            await self._call("getMyDescription", language_code=language_code)
        )

    async def set_my_short_description(
        self,
        *,
        short_description: Optional[str] = None,
        language_code: Optional[str] = None,
    ) -> bool:
        """Set the bot's short description, shown on the bot's profile page."""
        return bool(
            await self._call(
                "setMyShortDescription",
                short_description=short_description,
                language_code=language_code,
            )
        )

    async def get_my_short_description(
        self, *, language_code: Optional[str] = None
    ) -> BotShortDescription:
        """Get the bot's short description for the given language."""
        return BotShortDescription.from_dict(
            await self._call("getMyShortDescription", language_code=language_code)
        )

    async def get_forum_topic_icon_stickers(self) -> list[Sticker]:
        """List the custom emoji stickers allowed as forum topic icons."""
        result = await self._call("getForumTopicIconStickers")
        return [Sticker.from_dict(sticker) for sticker in result]

    async def create_forum_topic(
        self,
        chat_id: int | str,
        name: str,
        *,
        icon_color: Optional[int] = None,
        icon_custom_emoji_id: Optional[str] = None,
    ) -> ForumTopic:
        """Create a topic in a forum supergroup."""
        return ForumTopic.from_dict(
            await self._call(
                "createForumTopic",
                chat_id=chat_id,
                name=name,
                icon_color=icon_color,
                icon_custom_emoji_id=icon_custom_emoji_id,
            )
        )

    async def edit_forum_topic(
        self,
        chat_id: int | str,
        message_thread_id: int,
        *,
        name: Optional[str] = None,
        icon_custom_emoji_id: Optional[str] = None,
    ) -> bool:
        """Edit a forum topic's name or icon."""
        return bool(
            await self._call(
                "editForumTopic",
                chat_id=chat_id,
                message_thread_id=message_thread_id,
                name=name,
                icon_custom_emoji_id=icon_custom_emoji_id,
            )
        )

    async def close_forum_topic(
        self, chat_id: int | str, message_thread_id: int
    ) -> bool:
        """Close an open forum topic."""
        return bool(
            await self._call(
                "closeForumTopic",
                chat_id=chat_id,
                message_thread_id=message_thread_id,
            )
        )

    async def reopen_forum_topic(
        self, chat_id: int | str, message_thread_id: int
    ) -> bool:
        """Reopen a closed forum topic."""
        return bool(
            await self._call(
                "reopenForumTopic",
                chat_id=chat_id,
                message_thread_id=message_thread_id,
            )
        )

    async def delete_forum_topic(
        self, chat_id: int | str, message_thread_id: int
    ) -> bool:
        """Delete a forum topic along with all its messages."""
        return bool(
            await self._call(
                "deleteForumTopic",
                chat_id=chat_id,
                message_thread_id=message_thread_id,
            )
        )

    async def unpin_all_forum_topic_messages(
        self, chat_id: int | str, message_thread_id: int
    ) -> bool:
        """Unpin all messages in a forum topic."""
        return bool(
            await self._call(
                "unpinAllForumTopicMessages",
                chat_id=chat_id,
                message_thread_id=message_thread_id,
            )
        )

    async def edit_general_forum_topic(self, chat_id: int | str, name: str) -> bool:
        """Rename the 'General' topic of a forum."""
        return bool(
            await self._call("editGeneralForumTopic", chat_id=chat_id, name=name)
        )

    async def close_general_forum_topic(self, chat_id: int | str) -> bool:
        """Close the 'General' topic of a forum."""
        return bool(await self._call("closeGeneralForumTopic", chat_id=chat_id))

    async def reopen_general_forum_topic(self, chat_id: int | str) -> bool:
        """Reopen the 'General' topic of a forum."""
        return bool(await self._call("reopenGeneralForumTopic", chat_id=chat_id))

    async def hide_general_forum_topic(self, chat_id: int | str) -> bool:
        """Hide the 'General' topic of a forum."""
        return bool(await self._call("hideGeneralForumTopic", chat_id=chat_id))

    async def unhide_general_forum_topic(self, chat_id: int | str) -> bool:
        """Unhide the 'General' topic of a forum."""
        return bool(await self._call("unhideGeneralForumTopic", chat_id=chat_id))

    async def unpin_all_general_forum_topic_messages(self, chat_id: int | str) -> bool:
        """Unpin all messages in the 'General' topic of a forum."""
        return bool(
            await self._call("unpinAllGeneralForumTopicMessages", chat_id=chat_id)
        )

    async def get_sticker_set(self, name: str) -> StickerSet:
        """Fetch a sticker set by name."""
        return StickerSet.from_dict(await self._call("getStickerSet", name=name))

    async def get_custom_emoji_stickers(
        self, custom_emoji_ids: list[str]
    ) -> list[Sticker]:
        """Fetch the stickers for the given custom emoji ids."""
        result = await self._call(
            "getCustomEmojiStickers", custom_emoji_ids=custom_emoji_ids
        )
        return [Sticker.from_dict(sticker) for sticker in result]

    async def upload_sticker_file(
        self, user_id: int, sticker: FileInput, sticker_format: str
    ) -> File:
        """Upload a sticker file for later use in a sticker set."""
        return File.from_dict(
            await self._call(
                "uploadStickerFile",
                user_id=user_id,
                sticker=sticker,
                sticker_format=sticker_format,
            )
        )

    async def create_new_sticker_set(
        self,
        user_id: int,
        name: str,
        title: str,
        stickers: list[InputSticker],
        *,
        sticker_type: Optional[str] = None,
        needs_repainting: Optional[bool] = None,
    ) -> bool:
        """Create a new sticker set owned by a user."""
        return bool(
            await self._call(
                "createNewStickerSet",
                user_id=user_id,
                name=name,
                title=title,
                stickers=[
                    s.to_dict() if hasattr(s, "to_dict") else s for s in stickers
                ],
                sticker_type=sticker_type,
                needs_repainting=needs_repainting,
            )
        )

    async def add_sticker_to_set(
        self, user_id: int, name: str, sticker: InputSticker
    ) -> bool:
        """Add a sticker to an existing set owned by the bot."""
        return bool(
            await self._call(
                "addStickerToSet", user_id=user_id, name=name, sticker=sticker
            )
        )

    async def set_sticker_position_in_set(self, sticker: str, position: int) -> bool:
        """Move a sticker to a new position within its set."""
        return bool(
            await self._call(
                "setStickerPositionInSet", sticker=sticker, position=position
            )
        )

    async def delete_sticker_from_set(self, sticker: str) -> bool:
        """Remove a sticker from the set it belongs to."""
        return bool(await self._call("deleteStickerFromSet", sticker=sticker))

    async def replace_sticker_in_set(
        self, user_id: int, name: str, old_sticker: str, sticker: InputSticker
    ) -> bool:
        """Replace a sticker in a set with another one."""
        return bool(
            await self._call(
                "replaceStickerInSet",
                user_id=user_id,
                name=name,
                old_sticker=old_sticker,
                sticker=sticker,
            )
        )

    async def set_sticker_emoji_list(
        self, sticker: str, emoji_list: list[str]
    ) -> bool:
        """Set the emoji associated with a bot-owned sticker."""
        return bool(
            await self._call(
                "setStickerEmojiList", sticker=sticker, emoji_list=emoji_list
            )
        )

    async def set_sticker_keywords(
        self, sticker: str, *, keywords: Optional[list[str]] = None
    ) -> bool:
        """Set the search keywords for a bot-owned sticker."""
        return bool(
            await self._call(
                "setStickerKeywords", sticker=sticker, keywords=keywords
            )
        )

    async def set_sticker_mask_position(
        self, sticker: str, *, mask_position: Optional[MaskPosition] = None
    ) -> bool:
        """Set the mask position of a bot-owned mask sticker."""
        return bool(
            await self._call(
                "setStickerMaskPosition",
                sticker=sticker,
                mask_position=mask_position,
            )
        )

    async def set_sticker_set_title(self, name: str, title: str) -> bool:
        """Set the title of a sticker set."""
        return bool(
            await self._call("setStickerSetTitle", name=name, title=title)
        )

    async def set_sticker_set_thumbnail(
        self,
        name: str,
        user_id: int,
        format: str,
        *,
        thumbnail: Optional[FileInput] = None,
    ) -> bool:
        """Set the thumbnail of a sticker set; pass an InputFile to upload one."""
        return bool(
            await self._call(
                "setStickerSetThumbnail",
                name=name,
                user_id=user_id,
                format=format,
                thumbnail=thumbnail,
            )
        )

    async def set_custom_emoji_sticker_set_thumbnail(
        self, name: str, *, custom_emoji_id: Optional[str] = None
    ) -> bool:
        """Set the thumbnail of a custom emoji sticker set."""
        return bool(
            await self._call(
                "setCustomEmojiStickerSetThumbnail",
                name=name,
                custom_emoji_id=custom_emoji_id,
            )
        )

    async def delete_sticker_set(self, name: str) -> bool:
        """Delete a sticker set owned by the bot."""
        return bool(await self._call("deleteStickerSet", name=name))

    async def answer_inline_query(
        self,
        inline_query_id: str,
        results: list[InlineQueryResult],
        *,
        cache_time: Optional[int] = None,
        is_personal: Optional[bool] = None,
        next_offset: Optional[str] = None,
        button: Optional[dict[str, Any]] = None,
    ) -> bool:
        """Answer an inline query with a list of results."""
        return bool(
            await self._call(
                "answerInlineQuery",
                inline_query_id=inline_query_id,
                results=[
                    r.to_dict() if hasattr(r, "to_dict") else r for r in results
                ],
                cache_time=cache_time,
                is_personal=is_personal,
                next_offset=next_offset,
                button=button,
            )
        )

    async def answer_web_app_query(
        self, web_app_query_id: str, result: InlineQueryResult
    ) -> SentWebAppMessage:
        """Answer a Web App query with a single inline result."""
        return SentWebAppMessage.from_dict(
            await self._call(
                "answerWebAppQuery",
                web_app_query_id=web_app_query_id,
                result=result.to_dict() if hasattr(result, "to_dict") else result,
            )
        )


def _edited(result: Any) -> Message | bool:
    """Parse an editMessage* result: a Message, or True for inline edits."""
    return True if result is True else Message.from_dict(result)
