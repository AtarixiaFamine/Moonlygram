"""Typed models for Bot API objects.

Each type keeps the original response in a raw dict, so fields that are not
yet modelled stay reachable (for example message.raw["photo"]).

The Bot API sender field is named "from", a Python keyword, so it is exposed
as from_user.
"""
from __future__ import annotations

import os
from dataclasses import asdict, dataclass, field
from typing import IO, TYPE_CHECKING, Any, Optional, Union

if TYPE_CHECKING:
    from .bot import Bot


def _bound(obj: Any) -> "Bot":
    """Return the Bot an object was bound to, or raise if it was never bound."""
    bot: Optional[Bot] = obj._bot
    if bot is None:
        raise RuntimeError(
            f"{type(obj).__name__} is not bound to a Bot; shortcut methods work "
            "only on objects received from an Application-dispatched update."
        )
    return bot


@dataclass(slots=True)
class User:
    id: int
    is_bot: bool
    first_name: str
    username: Optional[str] = None
    last_name: Optional[str] = None
    _bot: "Optional[Bot]" = field(default=None, init=False, repr=False, compare=False)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "User":
        return cls(
            id=d["id"],
            is_bot=d.get("is_bot", False),
            first_name=d.get("first_name", ""),
            username=d.get("username"),
            last_name=d.get("last_name"),
        )

    def set_bot(self, bot: "Bot") -> None:
        self._bot = bot

    async def send_message(self, text: str, **kwargs: Any) -> "Message":
        """Send a direct message to this user."""
        return await _bound(self).send_message(self.id, text, **kwargs)


@dataclass(slots=True)
class Chat:
    id: int
    type: str
    title: Optional[str] = None
    username: Optional[str] = None
    _bot: "Optional[Bot]" = field(default=None, init=False, repr=False, compare=False)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Chat":
        return cls(
            id=d["id"],
            type=d["type"],
            title=d.get("title"),
            username=d.get("username"),
        )

    def set_bot(self, bot: "Bot") -> None:
        self._bot = bot

    async def send_message(self, text: str, **kwargs: Any) -> "Message":
        """Send a text message to this chat."""
        return await _bound(self).send_message(self.id, text, **kwargs)

    async def send_photo(self, photo: "FileInput", **kwargs: Any) -> "Message":
        """Send a photo to this chat."""
        return await _bound(self).send_photo(self.id, photo, **kwargs)


@dataclass(slots=True)
class MaskPosition:
    """Where a mask sticker is placed on a face (sent and received)."""

    point: str
    x_shift: float
    y_shift: float
    scale: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "point": self.point,
            "x_shift": self.x_shift,
            "y_shift": self.y_shift,
            "scale": self.scale,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "MaskPosition":
        return cls(
            point=d.get("point", ""),
            x_shift=d.get("x_shift", 0.0),
            y_shift=d.get("y_shift", 0.0),
            scale=d.get("scale", 0.0),
        )


@dataclass(slots=True)
class InputSticker:
    """A sticker to add to a set (sent).

    sticker is a file_id, an HTTP URL, or "attach://<name>" for an uploaded
    file; format is one of "static", "animated", or "video".
    """

    sticker: str
    format: str
    emoji_list: list[str]
    mask_position: Optional[MaskPosition] = None
    keywords: Optional[list[str]] = None

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "sticker": self.sticker,
            "format": self.format,
            "emoji_list": list(self.emoji_list),
        }
        if self.mask_position is not None:
            d["mask_position"] = self.mask_position.to_dict()
        if self.keywords is not None:
            d["keywords"] = list(self.keywords)
        return d


def _entities(raw: Optional[list[dict[str, Any]]]) -> Optional[list["MessageEntity"]]:
    return [MessageEntity.from_dict(e) for e in raw] if raw else None


@dataclass(slots=True)
class Message:
    message_id: int
    chat: Chat
    from_user: Optional[User] = None
    text: Optional[str] = None
    entities: Optional[list[MessageEntity]] = None
    caption: Optional[str] = None
    caption_entities: Optional[list[MessageEntity]] = None
    photo: Optional[list[PhotoSize]] = None
    document: Optional[Document] = None
    audio: Optional[Audio] = None
    video: Optional[Video] = None
    animation: Optional[Animation] = None
    voice: Optional[Voice] = None
    video_note: Optional[VideoNote] = None
    sticker: Optional[Sticker] = None
    location: Optional[Location] = None
    venue: Optional[Venue] = None
    contact: Optional[Contact] = None
    poll: Optional[Poll] = None
    dice: Optional[Dice] = None
    date: Optional[int] = None
    edit_date: Optional[int] = None
    message_thread_id: Optional[int] = None
    reply_to_message: Optional["Message"] = None
    via_bot: Optional[User] = None
    forward_origin: Optional[MessageOrigin] = None
    author_signature: Optional[str] = None
    has_protected_content: Optional[bool] = None
    is_automatic_forward: Optional[bool] = None
    new_chat_members: Optional[list[User]] = None
    left_chat_member: Optional[User] = None
    pinned_message: Optional["Message"] = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)
    _bot: "Optional[Bot]" = field(default=None, init=False, repr=False, compare=False)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Message":
        return cls(
            message_id=d["message_id"],
            chat=Chat.from_dict(d["chat"]),
            from_user=User.from_dict(d["from"]) if "from" in d else None,
            text=d.get("text"),
            entities=_entities(d.get("entities")),
            caption=d.get("caption"),
            caption_entities=_entities(d.get("caption_entities")),
            photo=[PhotoSize.from_dict(p) for p in d["photo"]] if "photo" in d else None,
            document=Document.from_dict(d["document"]) if "document" in d else None,
            audio=Audio.from_dict(d["audio"]) if "audio" in d else None,
            video=Video.from_dict(d["video"]) if "video" in d else None,
            animation=Animation.from_dict(d["animation"]) if "animation" in d else None,
            voice=Voice.from_dict(d["voice"]) if "voice" in d else None,
            video_note=VideoNote.from_dict(d["video_note"]) if "video_note" in d else None,
            sticker=Sticker.from_dict(d["sticker"]) if "sticker" in d else None,
            location=Location.from_dict(d["location"]) if "location" in d else None,
            venue=Venue.from_dict(d["venue"]) if "venue" in d else None,
            contact=Contact.from_dict(d["contact"]) if "contact" in d else None,
            poll=Poll.from_dict(d["poll"]) if "poll" in d else None,
            dice=Dice.from_dict(d["dice"]) if "dice" in d else None,
            date=d.get("date"),
            edit_date=d.get("edit_date"),
            message_thread_id=d.get("message_thread_id"),
            reply_to_message=(
                Message.from_dict(d["reply_to_message"])
                if "reply_to_message" in d
                else None
            ),
            via_bot=User.from_dict(d["via_bot"]) if "via_bot" in d else None,
            forward_origin=(
                MessageOrigin.from_dict(d["forward_origin"])
                if "forward_origin" in d
                else None
            ),
            author_signature=d.get("author_signature"),
            has_protected_content=d.get("has_protected_content"),
            is_automatic_forward=d.get("is_automatic_forward"),
            new_chat_members=(
                [User.from_dict(u) for u in d["new_chat_members"]]
                if "new_chat_members" in d
                else None
            ),
            left_chat_member=(
                User.from_dict(d["left_chat_member"])
                if "left_chat_member" in d
                else None
            ),
            pinned_message=(
                Message.from_dict(d["pinned_message"])
                if "pinned_message" in d
                else None
            ),
            raw=d,
        )

    def set_bot(self, bot: "Bot") -> None:
        self._bot = bot
        self.chat.set_bot(bot)
        if self.from_user is not None:
            self.from_user.set_bot(bot)
        if self.via_bot is not None:
            self.via_bot.set_bot(bot)
        if self.reply_to_message is not None:
            self.reply_to_message.set_bot(bot)
        if self.pinned_message is not None:
            self.pinned_message.set_bot(bot)
        for member in self.new_chat_members or ():
            member.set_bot(bot)
        if self.left_chat_member is not None:
            self.left_chat_member.set_bot(bot)

    async def reply_text(self, text: str, **kwargs: Any) -> "Message":
        """Send a text message to this message's chat."""
        return await _bound(self).send_message(self.chat.id, text, **kwargs)

    async def reply_photo(self, photo: FileInput, **kwargs: Any) -> "Message":
        """Send a photo to this message's chat."""
        return await _bound(self).send_photo(self.chat.id, photo, **kwargs)

    async def reply_document(self, document: FileInput, **kwargs: Any) -> "Message":
        """Send a document to this message's chat."""
        return await _bound(self).send_document(self.chat.id, document, **kwargs)

    async def edit_text(self, text: str, **kwargs: Any) -> Message | bool:
        """Edit this message's text."""
        return await _bound(self).edit_message_text(
            text, chat_id=self.chat.id, message_id=self.message_id, **kwargs
        )

    async def delete(self) -> bool:
        """Delete this message."""
        return await _bound(self).delete_message(self.chat.id, self.message_id)

    async def forward(self, chat_id: int | str, **kwargs: Any) -> "Message":
        """Forward this message to another chat."""
        return await _bound(self).forward_message(
            chat_id, self.chat.id, self.message_id, **kwargs
        )

    async def copy(self, chat_id: int | str, **kwargs: Any) -> MessageId:
        """Copy this message to another chat."""
        return await _bound(self).copy_message(
            chat_id, self.chat.id, self.message_id, **kwargs
        )


@dataclass(slots=True)
class CallbackQuery:
    """An incoming callback query from a button on an inline keyboard."""

    id: str
    from_user: User
    message: Optional[Message] = None
    data: Optional[str] = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)
    _bot: "Optional[Bot]" = field(default=None, init=False, repr=False, compare=False)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "CallbackQuery":
        return cls(
            id=d["id"],
            from_user=User.from_dict(d["from"]),
            message=Message.from_dict(d["message"]) if "message" in d else None,
            data=d.get("data"),
            raw=d,
        )

    def set_bot(self, bot: "Bot") -> None:
        self._bot = bot
        self.from_user.set_bot(bot)
        if self.message is not None:
            self.message.set_bot(bot)

    async def answer(
        self,
        text: Optional[str] = None,
        *,
        show_alert: Optional[bool] = None,
        **kwargs: Any,
    ) -> bool:
        """Answer this callback query with an optional toast or alert."""
        return await _bound(self).answer_callback_query(
            self.id, text=text, show_alert=show_alert, **kwargs
        )

    async def edit_message_text(self, text: str, **kwargs: Any) -> Message | bool:
        """Edit the message this query's button is attached to."""
        if self.message is not None:
            return await _bound(self).edit_message_text(
                text,
                chat_id=self.message.chat.id,
                message_id=self.message.message_id,
                **kwargs,
            )
        return await _bound(self).edit_message_text(
            text, inline_message_id=self.raw.get("inline_message_id"), **kwargs
        )


@dataclass(slots=True)
class InlineQuery:
    """An incoming inline query (the inline_query update)."""

    id: str
    from_user: User
    query: str
    offset: str
    chat_type: Optional[str] = None
    location: Optional[Location] = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)
    _bot: "Optional[Bot]" = field(default=None, init=False, repr=False, compare=False)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "InlineQuery":
        return cls(
            id=d["id"],
            from_user=User.from_dict(d["from"]),
            query=d["query"],
            offset=d["offset"],
            chat_type=d.get("chat_type"),
            location=Location.from_dict(d["location"]) if "location" in d else None,
            raw=d,
        )

    def set_bot(self, bot: "Bot") -> None:
        self._bot = bot
        self.from_user.set_bot(bot)

    async def answer(self, results: "list[InlineQueryResult]", **kwargs: Any) -> bool:
        """Answer this inline query with a list of results."""
        return await _bound(self).answer_inline_query(self.id, results, **kwargs)


@dataclass(slots=True)
class ChosenInlineResult:
    """A result the user chose from inline query results."""

    result_id: str
    from_user: User
    query: str
    location: Optional[Location] = None
    inline_message_id: Optional[str] = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "ChosenInlineResult":
        return cls(
            result_id=d["result_id"],
            from_user=User.from_dict(d["from"]),
            query=d["query"],
            location=Location.from_dict(d["location"]) if "location" in d else None,
            inline_message_id=d.get("inline_message_id"),
            raw=d,
        )


@dataclass(slots=True)
class Update:
    update_id: int
    message: Optional[Message] = None
    edited_message: Optional[Message] = None
    channel_post: Optional[Message] = None
    edited_channel_post: Optional[Message] = None
    callback_query: Optional[CallbackQuery] = None
    my_chat_member: Optional[ChatMemberUpdated] = None
    chat_member: Optional[ChatMemberUpdated] = None
    chat_join_request: Optional[ChatJoinRequest] = None
    inline_query: Optional[InlineQuery] = None
    chosen_inline_result: Optional[ChosenInlineResult] = None
    poll: Optional[Poll] = None
    poll_answer: Optional[PollAnswer] = None
    message_reaction: Optional[MessageReactionUpdated] = None
    message_reaction_count: Optional[MessageReactionCountUpdated] = None
    chat_boost: Optional[ChatBoostUpdated] = None
    removed_chat_boost: Optional[ChatBoostRemoved] = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Update":
        return cls(
            update_id=d["update_id"],
            message=Message.from_dict(d["message"]) if "message" in d else None,
            edited_message=(
                Message.from_dict(d["edited_message"])
                if "edited_message" in d
                else None
            ),
            channel_post=(
                Message.from_dict(d["channel_post"]) if "channel_post" in d else None
            ),
            edited_channel_post=(
                Message.from_dict(d["edited_channel_post"])
                if "edited_channel_post" in d
                else None
            ),
            callback_query=(
                CallbackQuery.from_dict(d["callback_query"])
                if "callback_query" in d
                else None
            ),
            my_chat_member=(
                ChatMemberUpdated.from_dict(d["my_chat_member"])
                if "my_chat_member" in d
                else None
            ),
            chat_member=(
                ChatMemberUpdated.from_dict(d["chat_member"])
                if "chat_member" in d
                else None
            ),
            chat_join_request=(
                ChatJoinRequest.from_dict(d["chat_join_request"])
                if "chat_join_request" in d
                else None
            ),
            inline_query=(
                InlineQuery.from_dict(d["inline_query"])
                if "inline_query" in d
                else None
            ),
            chosen_inline_result=(
                ChosenInlineResult.from_dict(d["chosen_inline_result"])
                if "chosen_inline_result" in d
                else None
            ),
            poll=Poll.from_dict(d["poll"]) if "poll" in d else None,
            poll_answer=(
                PollAnswer.from_dict(d["poll_answer"])
                if "poll_answer" in d
                else None
            ),
            message_reaction=(
                MessageReactionUpdated.from_dict(d["message_reaction"])
                if "message_reaction" in d
                else None
            ),
            message_reaction_count=(
                MessageReactionCountUpdated.from_dict(d["message_reaction_count"])
                if "message_reaction_count" in d
                else None
            ),
            chat_boost=(
                ChatBoostUpdated.from_dict(d["chat_boost"])
                if "chat_boost" in d
                else None
            ),
            removed_chat_boost=(
                ChatBoostRemoved.from_dict(d["removed_chat_boost"])
                if "removed_chat_boost" in d
                else None
            ),
            raw=d,
        )

    @property
    def effective_message(self) -> Optional[Message]:
        """The incoming message of this update, whatever message kind it is."""
        return (
            self.message
            or self.edited_message
            or self.channel_post
            or self.edited_channel_post
        )

    @property
    def effective_chat_id(self) -> Optional[int]:
        """The chat this update concerns, if any."""
        message = self.effective_message
        if message is not None:
            return message.chat.id
        if self.callback_query is not None and self.callback_query.message is not None:
            return self.callback_query.message.chat.id
        for membership in (self.my_chat_member, self.chat_member):
            if membership is not None:
                return membership.chat.id
        if self.chat_join_request is not None:
            return self.chat_join_request.chat.id
        if self.message_reaction is not None:
            return self.message_reaction.chat.id
        if self.message_reaction_count is not None:
            return self.message_reaction_count.chat.id
        if self.chat_boost is not None:
            return self.chat_boost.chat.id
        if self.removed_chat_boost is not None:
            return self.removed_chat_boost.chat.id
        if self.poll_answer is not None and self.poll_answer.voter_chat is not None:
            return self.poll_answer.voter_chat.id
        return None

    @property
    def effective_user_id(self) -> Optional[int]:
        """The user who caused this update, if any."""
        message = self.effective_message
        if message is not None and message.from_user is not None:
            return message.from_user.id
        if self.callback_query is not None:
            return self.callback_query.from_user.id
        for membership in (self.my_chat_member, self.chat_member):
            if membership is not None:
                return membership.from_user.id
        if self.chat_join_request is not None:
            return self.chat_join_request.from_user.id
        if self.inline_query is not None:
            return self.inline_query.from_user.id
        if self.chosen_inline_result is not None:
            return self.chosen_inline_result.from_user.id
        if self.poll_answer is not None and self.poll_answer.user is not None:
            return self.poll_answer.user.id
        if self.message_reaction is not None and self.message_reaction.user is not None:
            return self.message_reaction.user.id
        if self.chat_boost is not None and self.chat_boost.boost.source.user is not None:
            return self.chat_boost.boost.source.user.id
        if (
            self.removed_chat_boost is not None
            and self.removed_chat_boost.source.user is not None
        ):
            return self.removed_chat_boost.source.user.id
        return None

    def set_bot(self, bot: "Bot") -> None:
        """Bind a Bot onto this update and its children, enabling shortcuts."""
        for message in (
            self.message,
            self.edited_message,
            self.channel_post,
            self.edited_channel_post,
        ):
            if message is not None:
                message.set_bot(bot)
        if self.callback_query is not None:
            self.callback_query.set_bot(bot)
        for membership in (self.my_chat_member, self.chat_member):
            if membership is not None:
                membership.chat.set_bot(bot)
                membership.from_user.set_bot(bot)
        if self.chat_join_request is not None:
            self.chat_join_request.set_bot(bot)
        if self.inline_query is not None:
            self.inline_query.set_bot(bot)
        if self.chosen_inline_result is not None:
            self.chosen_inline_result.from_user.set_bot(bot)
        if self.poll_answer is not None:
            if self.poll_answer.user is not None:
                self.poll_answer.user.set_bot(bot)
            if self.poll_answer.voter_chat is not None:
                self.poll_answer.voter_chat.set_bot(bot)
        if self.message_reaction is not None:
            self.message_reaction.chat.set_bot(bot)
            if self.message_reaction.user is not None:
                self.message_reaction.user.set_bot(bot)
            if self.message_reaction.actor_chat is not None:
                self.message_reaction.actor_chat.set_bot(bot)
        if self.message_reaction_count is not None:
            self.message_reaction_count.chat.set_bot(bot)
        if self.chat_boost is not None:
            self.chat_boost.chat.set_bot(bot)
            if self.chat_boost.boost.source.user is not None:
                self.chat_boost.boost.source.user.set_bot(bot)
        if self.removed_chat_boost is not None:
            self.removed_chat_boost.chat.set_bot(bot)
            if self.removed_chat_boost.source.user is not None:
                self.removed_chat_boost.source.user.set_bot(bot)


@dataclass(slots=True)
class WebhookInfo:
    """The current webhook status, as returned by getWebhookInfo."""

    url: str
    has_custom_certificate: bool
    pending_update_count: int
    ip_address: Optional[str] = None
    last_error_date: Optional[int] = None
    last_error_message: Optional[str] = None
    max_connections: Optional[int] = None
    allowed_updates: Optional[list[str]] = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "WebhookInfo":
        return cls(
            url=d.get("url", ""),
            has_custom_certificate=d.get("has_custom_certificate", False),
            pending_update_count=d.get("pending_update_count", 0),
            ip_address=d.get("ip_address"),
            last_error_date=d.get("last_error_date"),
            last_error_message=d.get("last_error_message"),
            max_connections=d.get("max_connections"),
            allowed_updates=d.get("allowed_updates"),
            raw=d,
        )


@dataclass(slots=True)
class ChatPermissions:
    """The actions a non-admin member may take in a chat (used to restrict)."""

    can_send_messages: Optional[bool] = None
    can_send_audios: Optional[bool] = None
    can_send_documents: Optional[bool] = None
    can_send_photos: Optional[bool] = None
    can_send_videos: Optional[bool] = None
    can_send_video_notes: Optional[bool] = None
    can_send_voice_notes: Optional[bool] = None
    can_send_polls: Optional[bool] = None
    can_send_other_messages: Optional[bool] = None
    can_add_web_page_previews: Optional[bool] = None
    can_invite_users: Optional[bool] = None
    can_pin_messages: Optional[bool] = None
    can_change_info: Optional[bool] = None
    can_manage_topics: Optional[bool] = None

    def to_dict(self) -> dict[str, Any]:
        return {key: value for key, value in asdict(self).items() if value is not None}


@dataclass(slots=True)
class ChatAdministratorRights:
    """An administrator's rights in a chat.

    Sent to set_my_default_administrator_rights and returned by
    get_my_default_administrator_rights. Unset (None) rights are dropped when
    sent, which Telegram treats as not granted.
    """

    is_anonymous: Optional[bool] = None
    can_manage_chat: Optional[bool] = None
    can_delete_messages: Optional[bool] = None
    can_manage_video_chats: Optional[bool] = None
    can_restrict_members: Optional[bool] = None
    can_promote_members: Optional[bool] = None
    can_change_info: Optional[bool] = None
    can_invite_users: Optional[bool] = None
    can_post_stories: Optional[bool] = None
    can_edit_stories: Optional[bool] = None
    can_delete_stories: Optional[bool] = None
    can_post_messages: Optional[bool] = None
    can_edit_messages: Optional[bool] = None
    can_pin_messages: Optional[bool] = None
    can_manage_topics: Optional[bool] = None
    can_manage_direct_messages: Optional[bool] = None
    can_manage_tags: Optional[bool] = None

    def to_dict(self) -> dict[str, Any]:
        return {key: value for key, value in asdict(self).items() if value is not None}

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "ChatAdministratorRights":
        return cls(
            is_anonymous=d.get("is_anonymous"),
            can_manage_chat=d.get("can_manage_chat"),
            can_delete_messages=d.get("can_delete_messages"),
            can_manage_video_chats=d.get("can_manage_video_chats"),
            can_restrict_members=d.get("can_restrict_members"),
            can_promote_members=d.get("can_promote_members"),
            can_change_info=d.get("can_change_info"),
            can_invite_users=d.get("can_invite_users"),
            can_post_stories=d.get("can_post_stories"),
            can_edit_stories=d.get("can_edit_stories"),
            can_delete_stories=d.get("can_delete_stories"),
            can_post_messages=d.get("can_post_messages"),
            can_edit_messages=d.get("can_edit_messages"),
            can_pin_messages=d.get("can_pin_messages"),
            can_manage_topics=d.get("can_manage_topics"),
            can_manage_direct_messages=d.get("can_manage_direct_messages"),
            can_manage_tags=d.get("can_manage_tags"),
        )


@dataclass(slots=True)
class ChatJoinRequest:
    """A request to join a chat (the chat_join_request update)."""

    chat: Chat
    from_user: User
    user_chat_id: int
    date: int
    bio: Optional[str] = None
    invite_link: Optional[ChatInviteLink] = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)
    _bot: "Optional[Bot]" = field(default=None, init=False, repr=False, compare=False)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "ChatJoinRequest":
        return cls(
            chat=Chat.from_dict(d["chat"]),
            from_user=User.from_dict(d["from"]),
            user_chat_id=d["user_chat_id"],
            date=d["date"],
            bio=d.get("bio"),
            invite_link=(
                ChatInviteLink.from_dict(d["invite_link"])
                if "invite_link" in d
                else None
            ),
            raw=d,
        )

    def set_bot(self, bot: "Bot") -> None:
        self._bot = bot
        self.chat.set_bot(bot)
        self.from_user.set_bot(bot)

    async def approve(self) -> bool:
        """Approve this join request."""
        return await _bound(self).approve_chat_join_request(
            self.chat.id, self.from_user.id
        )

    async def decline(self) -> bool:
        """Decline this join request."""
        return await _bound(self).decline_chat_join_request(
            self.chat.id, self.from_user.id
        )


@dataclass(slots=True)
class BotCommand:
    """A bot command shown in the client's command menu."""

    command: str
    description: str

    def to_dict(self) -> dict[str, Any]:
        return {"command": self.command, "description": self.description}

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "BotCommand":
        return cls(command=d["command"], description=d["description"])


def _input_media_dict(
    media_type: str,
    media: str,
    caption: Optional[str],
    parse_mode: Optional[str],
    **extra: Any,
) -> dict[str, Any]:
    d: dict[str, Any] = {"type": media_type, "media": media}
    if caption is not None:
        d["caption"] = caption
    if parse_mode is not None:
        d["parse_mode"] = parse_mode
    for key, value in extra.items():
        if value is not None:
            d[key] = value
    return d


@dataclass(slots=True)
class InputMediaPhoto:
    """A photo for a media group or editMessageMedia (media is a file_id or URL)."""

    media: str
    caption: Optional[str] = None
    parse_mode: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return _input_media_dict("photo", self.media, self.caption, self.parse_mode)


@dataclass(slots=True)
class InputMediaVideo:
    """A video for a media group or editMessageMedia (media is a file_id or URL)."""

    media: str
    caption: Optional[str] = None
    parse_mode: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    duration: Optional[int] = None

    def to_dict(self) -> dict[str, Any]:
        return _input_media_dict(
            "video",
            self.media,
            self.caption,
            self.parse_mode,
            width=self.width,
            height=self.height,
            duration=self.duration,
        )


@dataclass(slots=True)
class InputMediaAudio:
    """An audio file for a media group or editMessageMedia."""

    media: str
    caption: Optional[str] = None
    parse_mode: Optional[str] = None
    duration: Optional[int] = None
    performer: Optional[str] = None
    title: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return _input_media_dict(
            "audio",
            self.media,
            self.caption,
            self.parse_mode,
            duration=self.duration,
            performer=self.performer,
            title=self.title,
        )


@dataclass(slots=True)
class InputMediaDocument:
    """A general file for a media group or editMessageMedia."""

    media: str
    caption: Optional[str] = None
    parse_mode: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return _input_media_dict("document", self.media, self.caption, self.parse_mode)


@dataclass(slots=True)
class InputMediaAnimation:
    """An animation for a media group or editMessageMedia."""

    media: str
    caption: Optional[str] = None
    parse_mode: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    duration: Optional[int] = None

    def to_dict(self) -> dict[str, Any]:
        return _input_media_dict(
            "animation",
            self.media,
            self.caption,
            self.parse_mode,
            width=self.width,
            height=self.height,
            duration=self.duration,
        )


@dataclass(slots=True)
class ReactionTypeEmoji:
    """An emoji reaction, e.g. ReactionTypeEmoji("\N{THUMBS UP SIGN}")."""

    emoji: str

    def to_dict(self) -> dict[str, Any]:
        return {"type": "emoji", "emoji": self.emoji}


@dataclass(slots=True)
class ReactionTypeCustomEmoji:
    """A custom emoji reaction, identified by its custom_emoji_id."""

    custom_emoji_id: str

    def to_dict(self) -> dict[str, Any]:
        return {"type": "custom_emoji", "custom_emoji_id": self.custom_emoji_id}


@dataclass(slots=True)
class ReactionTypePaid:
    """A paid (Telegram Star) reaction. It carries no extra fields."""

    def to_dict(self) -> dict[str, Any]:
        return {"type": "paid"}


def _reaction_type(d: dict[str, Any]) -> "ReactionType":
    """Parse one ReactionType dict into its typed variant, or keep it raw."""
    kind = d.get("type")
    if kind == "emoji":
        return ReactionTypeEmoji(emoji=d["emoji"])
    if kind == "custom_emoji":
        return ReactionTypeCustomEmoji(custom_emoji_id=d["custom_emoji_id"])
    if kind == "paid":
        return ReactionTypePaid()
    return d


def _reactions(items: Any) -> "list[ReactionType]":
    """Parse a list of ReactionType dicts, leaving unknown kinds as raw dicts."""
    return [_reaction_type(r) for r in items or ()]


class InputFile:
    """A local file to upload: raw bytes, a filesystem path, or a binary file object.

    The contents are read once at construction. Pass this as the media argument
    to send_photo, send_document, and similar to upload a new file; pass a plain
    string to reuse a file_id or to have Telegram fetch a URL.
    """

    __slots__ = ("content", "filename")

    def __init__(
        self,
        file: bytes | str | os.PathLike[str] | IO[bytes],
        filename: Optional[str] = None,
    ) -> None:
        if isinstance(file, (bytes, bytearray)):
            self.content = bytes(file)
            self.filename = filename or "file"
        elif hasattr(file, "read"):
            data = file.read()
            self.content = data if isinstance(data, bytes) else bytes(data)
            name = filename or getattr(file, "name", None) or "file"
            self.filename = os.path.basename(name)
        else:
            path = os.fspath(file)
            with open(path, "rb") as handle:
                self.content = handle.read()
            self.filename = filename or os.path.basename(path)


@dataclass(slots=True)
class InlineKeyboardButton:
    """A button on an inline keyboard. Set exactly one action (callback_data or url)."""

    text: str
    callback_data: Optional[str] = None
    url: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {"text": self.text}
        if self.callback_data is not None:
            d["callback_data"] = self.callback_data
        if self.url is not None:
            d["url"] = self.url
        return d


@dataclass(slots=True)
class InlineKeyboardMarkup:
    """An inline keyboard: rows of InlineKeyboardButton attached to a message."""

    inline_keyboard: list[list[InlineKeyboardButton]]

    def to_dict(self) -> dict[str, Any]:
        return {
            "inline_keyboard": [
                [button.to_dict() for button in row] for row in self.inline_keyboard
            ]
        }


@dataclass(slots=True)
class KeyboardButton:
    """A button on a custom reply keyboard."""

    text: str

    def to_dict(self) -> dict[str, Any]:
        return {"text": self.text}


@dataclass(slots=True)
class ReplyKeyboardMarkup:
    """A custom reply keyboard shown in place of the user's letter keyboard."""

    keyboard: list[list[KeyboardButton]]
    resize_keyboard: Optional[bool] = None
    one_time_keyboard: Optional[bool] = None

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "keyboard": [[button.to_dict() for button in row] for row in self.keyboard]
        }
        if self.resize_keyboard is not None:
            d["resize_keyboard"] = self.resize_keyboard
        if self.one_time_keyboard is not None:
            d["one_time_keyboard"] = self.one_time_keyboard
        return d


def _maybe_to_dict(value: Any) -> Any:
    """Serialize a value with a to_dict() method, else pass it through."""
    to_dict = getattr(value, "to_dict", None)
    return to_dict() if callable(to_dict) else value


def _inline_result_dict(
    type_: str,
    id_: str,
    *,
    reply_markup: Any = None,
    input_message_content: Any = None,
    **fields: Any,
) -> dict[str, Any]:
    d: dict[str, Any] = {"type": type_, "id": id_}
    for key, value in fields.items():
        if value is not None:
            d[key] = value
    if reply_markup is not None:
        d["reply_markup"] = _maybe_to_dict(reply_markup)
    if input_message_content is not None:
        d["input_message_content"] = _maybe_to_dict(input_message_content)
    return d


@dataclass(slots=True)
class InputTextMessageContent:
    """Text content for an inline query result's sent message."""

    message_text: str
    parse_mode: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {"message_text": self.message_text}
        if self.parse_mode is not None:
            d["parse_mode"] = self.parse_mode
        return d


@dataclass(slots=True)
class InlineQueryResultArticle:
    """An inline result linking to an article or web page."""

    id: str
    title: str
    input_message_content: "InputMessageContent"
    reply_markup: "Optional[InlineKeyboardMarkup]" = None
    url: Optional[str] = None
    description: Optional[str] = None
    thumbnail_url: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return _inline_result_dict(
            "article",
            self.id,
            title=self.title,
            url=self.url,
            description=self.description,
            thumbnail_url=self.thumbnail_url,
            reply_markup=self.reply_markup,
            input_message_content=self.input_message_content,
        )


@dataclass(slots=True)
class InlineQueryResultPhoto:
    """An inline result: a link to a photo (photo_url plus thumbnail_url)."""

    id: str
    photo_url: str
    thumbnail_url: str
    title: Optional[str] = None
    description: Optional[str] = None
    caption: Optional[str] = None
    parse_mode: Optional[str] = None
    reply_markup: "Optional[InlineKeyboardMarkup]" = None
    input_message_content: "Optional[InputMessageContent]" = None

    def to_dict(self) -> dict[str, Any]:
        return _inline_result_dict(
            "photo",
            self.id,
            photo_url=self.photo_url,
            thumbnail_url=self.thumbnail_url,
            title=self.title,
            description=self.description,
            caption=self.caption,
            parse_mode=self.parse_mode,
            reply_markup=self.reply_markup,
            input_message_content=self.input_message_content,
        )


@dataclass(slots=True)
class InlineQueryResultDocument:
    """An inline result: a link to a file (document_url plus mime_type)."""

    id: str
    title: str
    document_url: str
    mime_type: str
    caption: Optional[str] = None
    parse_mode: Optional[str] = None
    description: Optional[str] = None
    thumbnail_url: Optional[str] = None
    reply_markup: "Optional[InlineKeyboardMarkup]" = None
    input_message_content: "Optional[InputMessageContent]" = None

    def to_dict(self) -> dict[str, Any]:
        return _inline_result_dict(
            "document",
            self.id,
            title=self.title,
            document_url=self.document_url,
            mime_type=self.mime_type,
            caption=self.caption,
            parse_mode=self.parse_mode,
            description=self.description,
            thumbnail_url=self.thumbnail_url,
            reply_markup=self.reply_markup,
            input_message_content=self.input_message_content,
        )


@dataclass(slots=True)
class InlineQueryResultVideo:
    """An inline result: a link to a video (video_url, mime_type, thumbnail_url)."""

    id: str
    video_url: str
    mime_type: str
    thumbnail_url: str
    title: str
    caption: Optional[str] = None
    parse_mode: Optional[str] = None
    description: Optional[str] = None
    reply_markup: "Optional[InlineKeyboardMarkup]" = None
    input_message_content: "Optional[InputMessageContent]" = None

    def to_dict(self) -> dict[str, Any]:
        return _inline_result_dict(
            "video",
            self.id,
            video_url=self.video_url,
            mime_type=self.mime_type,
            thumbnail_url=self.thumbnail_url,
            title=self.title,
            caption=self.caption,
            parse_mode=self.parse_mode,
            description=self.description,
            reply_markup=self.reply_markup,
            input_message_content=self.input_message_content,
        )


@dataclass(slots=True)
class InlineQueryResultCachedPhoto:
    """An inline result: a photo stored on Telegram (photo_file_id)."""

    id: str
    photo_file_id: str
    title: Optional[str] = None
    description: Optional[str] = None
    caption: Optional[str] = None
    parse_mode: Optional[str] = None
    reply_markup: "Optional[InlineKeyboardMarkup]" = None
    input_message_content: "Optional[InputMessageContent]" = None

    def to_dict(self) -> dict[str, Any]:
        return _inline_result_dict(
            "photo",
            self.id,
            photo_file_id=self.photo_file_id,
            title=self.title,
            description=self.description,
            caption=self.caption,
            parse_mode=self.parse_mode,
            reply_markup=self.reply_markup,
            input_message_content=self.input_message_content,
        )


@dataclass(slots=True)
class InlineQueryResultCachedDocument:
    """An inline result: a file stored on Telegram (document_file_id)."""

    id: str
    title: str
    document_file_id: str
    description: Optional[str] = None
    caption: Optional[str] = None
    parse_mode: Optional[str] = None
    reply_markup: "Optional[InlineKeyboardMarkup]" = None
    input_message_content: "Optional[InputMessageContent]" = None

    def to_dict(self) -> dict[str, Any]:
        return _inline_result_dict(
            "document",
            self.id,
            title=self.title,
            document_file_id=self.document_file_id,
            description=self.description,
            caption=self.caption,
            parse_mode=self.parse_mode,
            reply_markup=self.reply_markup,
            input_message_content=self.input_message_content,
        )


@dataclass(slots=True)
class InlineQueryResultCachedVideo:
    """An inline result: a video stored on Telegram (video_file_id)."""

    id: str
    video_file_id: str
    title: str
    description: Optional[str] = None
    caption: Optional[str] = None
    parse_mode: Optional[str] = None
    reply_markup: "Optional[InlineKeyboardMarkup]" = None
    input_message_content: "Optional[InputMessageContent]" = None

    def to_dict(self) -> dict[str, Any]:
        return _inline_result_dict(
            "video",
            self.id,
            video_file_id=self.video_file_id,
            title=self.title,
            description=self.description,
            caption=self.caption,
            parse_mode=self.parse_mode,
            reply_markup=self.reply_markup,
            input_message_content=self.input_message_content,
        )


@dataclass(slots=True)
class InlineQueryResultCachedSticker:
    """An inline result: a sticker stored on Telegram (sticker_file_id)."""

    id: str
    sticker_file_id: str
    reply_markup: "Optional[InlineKeyboardMarkup]" = None
    input_message_content: "Optional[InputMessageContent]" = None

    def to_dict(self) -> dict[str, Any]:
        return _inline_result_dict(
            "sticker",
            self.id,
            sticker_file_id=self.sticker_file_id,
            reply_markup=self.reply_markup,
            input_message_content=self.input_message_content,
        )


ReplyMarkup = Union[InlineKeyboardMarkup, ReplyKeyboardMarkup, dict[str, Any]]

#: A file argument: an InputFile to upload, or a string file_id / URL.
FileInput = Union["InputFile", str]

#: A media item for send_media_group / edit_message_media (or a raw dict).
InputMedia = Union[
    InputMediaPhoto,
    InputMediaVideo,
    InputMediaAudio,
    InputMediaDocument,
    InputMediaAnimation,
    dict[str, Any],
]

#: A reaction (set on / received from a message), or a raw dict for an unknown kind.
ReactionType = Union[
    ReactionTypeEmoji,
    ReactionTypeCustomEmoji,
    ReactionTypePaid,
    dict[str, Any],
]

#: Content for an inline result's sent message (or a raw dict).
InputMessageContent = Union[InputTextMessageContent, dict[str, Any]]

#: An inline query result for answer_inline_query (or a raw dict for the long tail).
InlineQueryResult = Union[
    InlineQueryResultArticle,
    InlineQueryResultPhoto,
    InlineQueryResultDocument,
    InlineQueryResultVideo,
    InlineQueryResultCachedPhoto,
    InlineQueryResultCachedDocument,
    InlineQueryResultCachedVideo,
    InlineQueryResultCachedSticker,
    dict[str, Any],
]


# Data-only received types are generated from the Bot API spec by
# codegen/gen_types.py; they are re-exported here so the public import
# surface (moonlygram.types) is unchanged. Edit codegen/overrides.py to
# change what is modelled, then re-run the generator.
from ._types_generated import (  # noqa: E402
    Animation as Animation,
    Audio as Audio,
    BotDescription as BotDescription,
    BotName as BotName,
    BotShortDescription as BotShortDescription,
    ChatBoost as ChatBoost,
    ChatBoostRemoved as ChatBoostRemoved,
    ChatBoostSource as ChatBoostSource,
    ChatBoostUpdated as ChatBoostUpdated,
    ChatInviteLink as ChatInviteLink,
    ChatMember as ChatMember,
    ChatMemberUpdated as ChatMemberUpdated,
    Contact as Contact,
    Dice as Dice,
    Document as Document,
    File as File,
    ForumTopic as ForumTopic,
    Location as Location,
    MessageEntity as MessageEntity,
    MessageId as MessageId,
    MessageOrigin as MessageOrigin,
    MessageReactionCountUpdated as MessageReactionCountUpdated,
    MessageReactionUpdated as MessageReactionUpdated,
    PhotoSize as PhotoSize,
    Poll as Poll,
    PollAnswer as PollAnswer,
    PollOption as PollOption,
    ReactionCount as ReactionCount,
    SentWebAppMessage as SentWebAppMessage,
    Sticker as Sticker,
    StickerSet as StickerSet,
    UserChatBoosts as UserChatBoosts,
    UserProfilePhotos as UserProfilePhotos,
    Venue as Venue,
    Video as Video,
    VideoNote as VideoNote,
    Voice as Voice,
)
