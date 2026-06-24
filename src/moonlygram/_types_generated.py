"""Generated Bot API data types — do not edit by hand.

Produced by codegen/gen_types.py from Bot API 10.1.
Edit codegen/overrides.py and re-run the generator instead.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from .types import (  # noqa: E402
    Chat as Chat,
    MaskPosition as MaskPosition,
    ReactionType as ReactionType,
    User as User,
    _reaction_type as _reaction_type,
    _reactions as _reactions,
)


@dataclass(slots=True)
class Animation:
    """This object represents an animation file (GIF or H.264/MPEG-4 AVC video without
    sound).
    """

    file_id: str
    file_unique_id: str
    width: int
    height: int
    duration: int
    thumbnail: Optional[PhotoSize] = None
    file_name: Optional[str] = None
    mime_type: Optional[str] = None
    file_size: Optional[int] = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False, compare=False)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Animation":
        return cls(
            file_id=d.get("file_id"),
            file_unique_id=d.get("file_unique_id"),
            width=d.get("width"),
            height=d.get("height"),
            duration=d.get("duration"),
            thumbnail=PhotoSize.from_dict(d["thumbnail"]) if "thumbnail" in d else None,
            file_name=d.get("file_name"),
            mime_type=d.get("mime_type"),
            file_size=d.get("file_size"),
            raw=d,
        )


@dataclass(slots=True)
class Audio:
    """This object represents an audio file to be treated as music by the Telegram
    clients.
    """

    file_id: str
    file_unique_id: str
    duration: int
    performer: Optional[str] = None
    title: Optional[str] = None
    file_name: Optional[str] = None
    mime_type: Optional[str] = None
    file_size: Optional[int] = None
    thumbnail: Optional[PhotoSize] = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False, compare=False)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Audio":
        return cls(
            file_id=d.get("file_id"),
            file_unique_id=d.get("file_unique_id"),
            duration=d.get("duration"),
            performer=d.get("performer"),
            title=d.get("title"),
            file_name=d.get("file_name"),
            mime_type=d.get("mime_type"),
            file_size=d.get("file_size"),
            thumbnail=PhotoSize.from_dict(d["thumbnail"]) if "thumbnail" in d else None,
            raw=d,
        )


@dataclass(slots=True)
class BotDescription:
    """This object represents the bot's description."""

    description: str
    raw: dict[str, Any] = field(default_factory=dict, repr=False, compare=False)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "BotDescription":
        return cls(
            description=d.get("description"),
            raw=d,
        )


@dataclass(slots=True)
class BotName:
    """This object represents the bot's name."""

    name: str
    raw: dict[str, Any] = field(default_factory=dict, repr=False, compare=False)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "BotName":
        return cls(
            name=d.get("name"),
            raw=d,
        )


@dataclass(slots=True)
class BotShortDescription:
    """This object represents the bot's short description."""

    short_description: str
    raw: dict[str, Any] = field(default_factory=dict, repr=False, compare=False)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "BotShortDescription":
        return cls(
            short_description=d.get("short_description"),
            raw=d,
        )


@dataclass(slots=True)
class ChatBoost:
    """This object contains information about a chat boost."""

    boost_id: str
    add_date: int
    expiration_date: int
    source: ChatBoostSource
    raw: dict[str, Any] = field(default_factory=dict, repr=False, compare=False)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "ChatBoost":
        return cls(
            boost_id=d.get("boost_id"),
            add_date=d.get("add_date"),
            expiration_date=d.get("expiration_date"),
            source=ChatBoostSource.from_dict(d["source"]) if "source" in d else None,
            raw=d,
        )


@dataclass(slots=True)
class ChatBoostRemoved:
    """This object represents a boost removed from a chat."""

    chat: Chat
    boost_id: str
    remove_date: int
    source: ChatBoostSource
    raw: dict[str, Any] = field(default_factory=dict, repr=False, compare=False)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "ChatBoostRemoved":
        return cls(
            chat=Chat.from_dict(d["chat"]) if "chat" in d else None,
            boost_id=d.get("boost_id"),
            remove_date=d.get("remove_date"),
            source=ChatBoostSource.from_dict(d["source"]) if "source" in d else None,
            raw=d,
        )


@dataclass(slots=True)
class ChatBoostSource:
    """This object describes the source of a chat boost. It can be one of -
    ChatBoostSourcePremium - ChatBoostSourceGiftCode - ChatBoostSourceGiveaway
    """

    source: str
    user: Optional[User] = None
    giveaway_message_id: Optional[int] = None
    prize_star_count: Optional[int] = None
    is_unclaimed: Optional[bool] = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False, compare=False)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "ChatBoostSource":
        return cls(
            source=d.get("source"),
            user=User.from_dict(d["user"]) if "user" in d else None,
            giveaway_message_id=d.get("giveaway_message_id"),
            prize_star_count=d.get("prize_star_count"),
            is_unclaimed=d.get("is_unclaimed"),
            raw=d,
        )


@dataclass(slots=True)
class ChatBoostUpdated:
    """This object represents a boost added to a chat or changed."""

    chat: Chat
    boost: ChatBoost
    raw: dict[str, Any] = field(default_factory=dict, repr=False, compare=False)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "ChatBoostUpdated":
        return cls(
            chat=Chat.from_dict(d["chat"]) if "chat" in d else None,
            boost=ChatBoost.from_dict(d["boost"]) if "boost" in d else None,
            raw=d,
        )


@dataclass(slots=True)
class ChatInviteLink:
    """Represents an invite link for a chat."""

    invite_link: str
    creator: User
    creates_join_request: bool
    is_primary: bool
    is_revoked: bool
    name: Optional[str] = None
    expire_date: Optional[int] = None
    member_limit: Optional[int] = None
    pending_join_request_count: Optional[int] = None
    subscription_period: Optional[int] = None
    subscription_price: Optional[int] = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False, compare=False)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "ChatInviteLink":
        return cls(
            invite_link=d.get("invite_link"),
            creator=User.from_dict(d["creator"]) if "creator" in d else None,
            creates_join_request=d.get("creates_join_request"),
            is_primary=d.get("is_primary"),
            is_revoked=d.get("is_revoked"),
            name=d.get("name"),
            expire_date=d.get("expire_date"),
            member_limit=d.get("member_limit"),
            pending_join_request_count=d.get("pending_join_request_count"),
            subscription_period=d.get("subscription_period"),
            subscription_price=d.get("subscription_price"),
            raw=d,
        )


@dataclass(slots=True)
class ChatMember:
    """This object contains information about one member of a chat. Currently, the
    following 6 types of chat members are supported: - ChatMemberOwner -
    ChatMemberAdministrator - ChatMemberMember - ChatMemberRestricted -
    ChatMemberLeft - ChatMemberBanned
    """

    status: str
    user: User
    is_anonymous: Optional[bool] = None
    custom_title: Optional[str] = None
    can_be_edited: Optional[bool] = None
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
    tag: Optional[str] = None
    until_date: Optional[int] = None
    is_member: Optional[bool] = None
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
    can_react_to_messages: Optional[bool] = None
    can_edit_tag: Optional[bool] = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False, compare=False)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "ChatMember":
        return cls(
            status=d.get("status"),
            user=User.from_dict(d["user"]) if "user" in d else None,
            is_anonymous=d.get("is_anonymous"),
            custom_title=d.get("custom_title"),
            can_be_edited=d.get("can_be_edited"),
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
            tag=d.get("tag"),
            until_date=d.get("until_date"),
            is_member=d.get("is_member"),
            can_send_messages=d.get("can_send_messages"),
            can_send_audios=d.get("can_send_audios"),
            can_send_documents=d.get("can_send_documents"),
            can_send_photos=d.get("can_send_photos"),
            can_send_videos=d.get("can_send_videos"),
            can_send_video_notes=d.get("can_send_video_notes"),
            can_send_voice_notes=d.get("can_send_voice_notes"),
            can_send_polls=d.get("can_send_polls"),
            can_send_other_messages=d.get("can_send_other_messages"),
            can_add_web_page_previews=d.get("can_add_web_page_previews"),
            can_react_to_messages=d.get("can_react_to_messages"),
            can_edit_tag=d.get("can_edit_tag"),
            raw=d,
        )


@dataclass(slots=True)
class ChatMemberUpdated:
    """This object represents changes in the status of a chat member."""

    chat: Chat
    from_user: User
    date: int
    old_chat_member: ChatMember
    new_chat_member: ChatMember
    invite_link: Optional[ChatInviteLink] = None
    via_join_request: Optional[bool] = None
    via_chat_folder_invite_link: Optional[bool] = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False, compare=False)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "ChatMemberUpdated":
        return cls(
            chat=Chat.from_dict(d["chat"]) if "chat" in d else None,
            from_user=User.from_dict(d["from"]) if "from" in d else None,
            date=d.get("date"),
            old_chat_member=ChatMember.from_dict(d["old_chat_member"]) if "old_chat_member" in d else None,
            new_chat_member=ChatMember.from_dict(d["new_chat_member"]) if "new_chat_member" in d else None,
            invite_link=ChatInviteLink.from_dict(d["invite_link"]) if "invite_link" in d else None,
            via_join_request=d.get("via_join_request"),
            via_chat_folder_invite_link=d.get("via_chat_folder_invite_link"),
            raw=d,
        )


@dataclass(slots=True)
class Contact:
    """This object represents a phone contact."""

    phone_number: str
    first_name: str
    last_name: Optional[str] = None
    user_id: Optional[int] = None
    vcard: Optional[str] = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False, compare=False)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Contact":
        return cls(
            phone_number=d.get("phone_number"),
            first_name=d.get("first_name"),
            last_name=d.get("last_name"),
            user_id=d.get("user_id"),
            vcard=d.get("vcard"),
            raw=d,
        )


@dataclass(slots=True)
class Dice:
    """This object represents an animated emoji that displays a random value."""

    emoji: str
    value: int
    raw: dict[str, Any] = field(default_factory=dict, repr=False, compare=False)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Dice":
        return cls(
            emoji=d.get("emoji"),
            value=d.get("value"),
            raw=d,
        )


@dataclass(slots=True)
class Document:
    """This object represents a general file (as opposed to photos, voice messages and
    audio files).
    """

    file_id: str
    file_unique_id: str
    thumbnail: Optional[PhotoSize] = None
    file_name: Optional[str] = None
    mime_type: Optional[str] = None
    file_size: Optional[int] = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False, compare=False)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Document":
        return cls(
            file_id=d.get("file_id"),
            file_unique_id=d.get("file_unique_id"),
            thumbnail=PhotoSize.from_dict(d["thumbnail"]) if "thumbnail" in d else None,
            file_name=d.get("file_name"),
            mime_type=d.get("mime_type"),
            file_size=d.get("file_size"),
            raw=d,
        )


@dataclass(slots=True)
class File:
    """This object represents a file ready to be downloaded. The file can be
    downloaded via the link https://api.telegram.org/file/bot<token>/<file_path>.
    It is guaranteed that the link will be valid for at least 1 hour. When the link
    expires, a new one can be requested by calling getFile.
    """

    file_id: str
    file_unique_id: str
    file_size: Optional[int] = None
    file_path: Optional[str] = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False, compare=False)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "File":
        return cls(
            file_id=d.get("file_id"),
            file_unique_id=d.get("file_unique_id"),
            file_size=d.get("file_size"),
            file_path=d.get("file_path"),
            raw=d,
        )


@dataclass(slots=True)
class ForumTopic:
    """This object represents a forum topic."""

    message_thread_id: int
    name: str
    icon_color: int
    icon_custom_emoji_id: Optional[str] = None
    is_name_implicit: Optional[bool] = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False, compare=False)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "ForumTopic":
        return cls(
            message_thread_id=d.get("message_thread_id"),
            name=d.get("name"),
            icon_color=d.get("icon_color"),
            icon_custom_emoji_id=d.get("icon_custom_emoji_id"),
            is_name_implicit=d.get("is_name_implicit"),
            raw=d,
        )


@dataclass(slots=True)
class Location:
    """This object represents a point on the map."""

    latitude: float
    longitude: float
    horizontal_accuracy: Optional[float] = None
    live_period: Optional[int] = None
    heading: Optional[int] = None
    proximity_alert_radius: Optional[int] = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False, compare=False)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Location":
        return cls(
            latitude=d.get("latitude"),
            longitude=d.get("longitude"),
            horizontal_accuracy=d.get("horizontal_accuracy"),
            live_period=d.get("live_period"),
            heading=d.get("heading"),
            proximity_alert_radius=d.get("proximity_alert_radius"),
            raw=d,
        )


@dataclass(slots=True)
class MessageEntity:
    """This object represents one special entity in a text message. For example,
    hashtags, usernames, URLs, etc.
    """

    type: str
    offset: int
    length: int
    url: Optional[str] = None
    user: Optional[User] = None
    language: Optional[str] = None
    custom_emoji_id: Optional[str] = None
    unix_time: Optional[int] = None
    date_time_format: Optional[str] = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False, compare=False)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "MessageEntity":
        return cls(
            type=d.get("type"),
            offset=d.get("offset"),
            length=d.get("length"),
            url=d.get("url"),
            user=User.from_dict(d["user"]) if "user" in d else None,
            language=d.get("language"),
            custom_emoji_id=d.get("custom_emoji_id"),
            unix_time=d.get("unix_time"),
            date_time_format=d.get("date_time_format"),
            raw=d,
        )


@dataclass(slots=True)
class MessageId:
    """This object represents a unique message identifier."""

    message_id: int
    raw: dict[str, Any] = field(default_factory=dict, repr=False, compare=False)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "MessageId":
        return cls(
            message_id=d.get("message_id"),
            raw=d,
        )


@dataclass(slots=True)
class MessageOrigin:
    """This object describes the origin of a message. It can be one of -
    MessageOriginUser - MessageOriginHiddenUser - MessageOriginChat -
    MessageOriginChannel
    """

    type: str
    date: int
    sender_user: Optional[User] = None
    sender_user_name: Optional[str] = None
    sender_chat: Optional[Chat] = None
    author_signature: Optional[str] = None
    chat: Optional[Chat] = None
    message_id: Optional[int] = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False, compare=False)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "MessageOrigin":
        return cls(
            type=d.get("type"),
            date=d.get("date"),
            sender_user=User.from_dict(d["sender_user"]) if "sender_user" in d else None,
            sender_user_name=d.get("sender_user_name"),
            sender_chat=Chat.from_dict(d["sender_chat"]) if "sender_chat" in d else None,
            author_signature=d.get("author_signature"),
            chat=Chat.from_dict(d["chat"]) if "chat" in d else None,
            message_id=d.get("message_id"),
            raw=d,
        )


@dataclass(slots=True)
class MessageReactionCountUpdated:
    """This object represents reaction changes on a message with anonymous reactions."""

    chat: Chat
    message_id: int
    date: int
    reactions: list[ReactionCount]
    raw: dict[str, Any] = field(default_factory=dict, repr=False, compare=False)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "MessageReactionCountUpdated":
        return cls(
            chat=Chat.from_dict(d["chat"]) if "chat" in d else None,
            message_id=d.get("message_id"),
            date=d.get("date"),
            reactions=[ReactionCount.from_dict(i) for i in d["reactions"]] if "reactions" in d else None,
            raw=d,
        )


@dataclass(slots=True)
class MessageReactionUpdated:
    """This object represents a change of a reaction on a message performed by a user."""

    chat: Chat
    message_id: int
    date: int
    old_reaction: list[ReactionType]
    new_reaction: list[ReactionType]
    user: Optional[User] = None
    actor_chat: Optional[Chat] = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False, compare=False)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "MessageReactionUpdated":
        return cls(
            chat=Chat.from_dict(d["chat"]) if "chat" in d else None,
            message_id=d.get("message_id"),
            date=d.get("date"),
            old_reaction=_reactions(d.get("old_reaction")),
            new_reaction=_reactions(d.get("new_reaction")),
            user=User.from_dict(d["user"]) if "user" in d else None,
            actor_chat=Chat.from_dict(d["actor_chat"]) if "actor_chat" in d else None,
            raw=d,
        )


@dataclass(slots=True)
class PhotoSize:
    """This object represents one size of a photo or a file / sticker thumbnail."""

    file_id: str
    file_unique_id: str
    width: int
    height: int
    file_size: Optional[int] = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False, compare=False)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "PhotoSize":
        return cls(
            file_id=d.get("file_id"),
            file_unique_id=d.get("file_unique_id"),
            width=d.get("width"),
            height=d.get("height"),
            file_size=d.get("file_size"),
            raw=d,
        )


@dataclass(slots=True)
class Poll:
    """This object contains information about a poll."""

    id: str
    question: str
    options: list[PollOption]
    total_voter_count: int
    is_closed: bool
    is_anonymous: bool
    type: str
    allows_multiple_answers: bool
    allows_revoting: bool
    members_only: bool
    question_entities: Optional[list[MessageEntity]] = None
    country_codes: Optional[list[str]] = None
    correct_option_ids: Optional[list[int]] = None
    explanation: Optional[str] = None
    explanation_entities: Optional[list[MessageEntity]] = None
    explanation_media: Optional[dict[str, Any]] = None
    open_period: Optional[int] = None
    close_date: Optional[int] = None
    description: Optional[str] = None
    description_entities: Optional[list[MessageEntity]] = None
    media: Optional[dict[str, Any]] = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False, compare=False)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Poll":
        return cls(
            id=d.get("id"),
            question=d.get("question"),
            options=[PollOption.from_dict(i) for i in d["options"]] if "options" in d else None,
            total_voter_count=d.get("total_voter_count"),
            is_closed=d.get("is_closed"),
            is_anonymous=d.get("is_anonymous"),
            type=d.get("type"),
            allows_multiple_answers=d.get("allows_multiple_answers"),
            allows_revoting=d.get("allows_revoting"),
            members_only=d.get("members_only"),
            question_entities=[MessageEntity.from_dict(i) for i in d["question_entities"]] if "question_entities" in d else None,
            country_codes=d.get("country_codes"),
            correct_option_ids=d.get("correct_option_ids"),
            explanation=d.get("explanation"),
            explanation_entities=[MessageEntity.from_dict(i) for i in d["explanation_entities"]] if "explanation_entities" in d else None,
            explanation_media=d.get("explanation_media"),
            open_period=d.get("open_period"),
            close_date=d.get("close_date"),
            description=d.get("description"),
            description_entities=[MessageEntity.from_dict(i) for i in d["description_entities"]] if "description_entities" in d else None,
            media=d.get("media"),
            raw=d,
        )


@dataclass(slots=True)
class PollAnswer:
    """This object represents an answer of a user in a non-anonymous poll."""

    poll_id: str
    option_ids: list[int]
    option_persistent_ids: list[str]
    voter_chat: Optional[Chat] = None
    user: Optional[User] = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False, compare=False)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "PollAnswer":
        return cls(
            poll_id=d.get("poll_id"),
            option_ids=d.get("option_ids"),
            option_persistent_ids=d.get("option_persistent_ids"),
            voter_chat=Chat.from_dict(d["voter_chat"]) if "voter_chat" in d else None,
            user=User.from_dict(d["user"]) if "user" in d else None,
            raw=d,
        )


@dataclass(slots=True)
class PollOption:
    """This object contains information about one answer option in a poll."""

    persistent_id: str
    text: str
    voter_count: int
    text_entities: Optional[list[MessageEntity]] = None
    media: Optional[dict[str, Any]] = None
    added_by_user: Optional[User] = None
    added_by_chat: Optional[Chat] = None
    addition_date: Optional[int] = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False, compare=False)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "PollOption":
        return cls(
            persistent_id=d.get("persistent_id"),
            text=d.get("text"),
            voter_count=d.get("voter_count"),
            text_entities=[MessageEntity.from_dict(i) for i in d["text_entities"]] if "text_entities" in d else None,
            media=d.get("media"),
            added_by_user=User.from_dict(d["added_by_user"]) if "added_by_user" in d else None,
            added_by_chat=Chat.from_dict(d["added_by_chat"]) if "added_by_chat" in d else None,
            addition_date=d.get("addition_date"),
            raw=d,
        )


@dataclass(slots=True)
class ReactionCount:
    """Represents a reaction added to a message along with the number of times it was
    added.
    """

    type: ReactionType
    total_count: int
    raw: dict[str, Any] = field(default_factory=dict, repr=False, compare=False)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "ReactionCount":
        return cls(
            type=_reaction_type(d.get("type", {})),
            total_count=d.get("total_count"),
            raw=d,
        )


@dataclass(slots=True)
class SentWebAppMessage:
    """Describes an inline message sent by a Web App on behalf of a user."""

    inline_message_id: Optional[str] = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False, compare=False)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "SentWebAppMessage":
        return cls(
            inline_message_id=d.get("inline_message_id"),
            raw=d,
        )


@dataclass(slots=True)
class Sticker:
    """This object represents a sticker."""

    file_id: str
    file_unique_id: str
    type: str
    width: int
    height: int
    is_animated: bool
    is_video: bool
    thumbnail: Optional[PhotoSize] = None
    emoji: Optional[str] = None
    set_name: Optional[str] = None
    premium_animation: Optional[File] = None
    mask_position: Optional[MaskPosition] = None
    custom_emoji_id: Optional[str] = None
    needs_repainting: Optional[bool] = None
    file_size: Optional[int] = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False, compare=False)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Sticker":
        return cls(
            file_id=d.get("file_id"),
            file_unique_id=d.get("file_unique_id"),
            type=d.get("type"),
            width=d.get("width"),
            height=d.get("height"),
            is_animated=d.get("is_animated"),
            is_video=d.get("is_video"),
            thumbnail=PhotoSize.from_dict(d["thumbnail"]) if "thumbnail" in d else None,
            emoji=d.get("emoji"),
            set_name=d.get("set_name"),
            premium_animation=File.from_dict(d["premium_animation"]) if "premium_animation" in d else None,
            mask_position=MaskPosition.from_dict(d["mask_position"]) if "mask_position" in d else None,
            custom_emoji_id=d.get("custom_emoji_id"),
            needs_repainting=d.get("needs_repainting"),
            file_size=d.get("file_size"),
            raw=d,
        )


@dataclass(slots=True)
class StickerSet:
    """This object represents a sticker set."""

    name: str
    title: str
    sticker_type: str
    stickers: list[Sticker]
    thumbnail: Optional[PhotoSize] = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False, compare=False)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "StickerSet":
        return cls(
            name=d.get("name"),
            title=d.get("title"),
            sticker_type=d.get("sticker_type"),
            stickers=[Sticker.from_dict(i) for i in d["stickers"]] if "stickers" in d else None,
            thumbnail=PhotoSize.from_dict(d["thumbnail"]) if "thumbnail" in d else None,
            raw=d,
        )


@dataclass(slots=True)
class UserChatBoosts:
    """This object represents a list of boosts added to a chat by a user."""

    boosts: list[ChatBoost]
    raw: dict[str, Any] = field(default_factory=dict, repr=False, compare=False)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "UserChatBoosts":
        return cls(
            boosts=[ChatBoost.from_dict(i) for i in d["boosts"]] if "boosts" in d else None,
            raw=d,
        )


@dataclass(slots=True)
class UserProfilePhotos:
    """This object represent a user's profile pictures."""

    total_count: int
    photos: list[list[PhotoSize]]
    raw: dict[str, Any] = field(default_factory=dict, repr=False, compare=False)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "UserProfilePhotos":
        return cls(
            total_count=d.get("total_count"),
            photos=[[PhotoSize.from_dict(j) for j in i] for i in d["photos"]] if "photos" in d else None,
            raw=d,
        )


@dataclass(slots=True)
class Venue:
    """This object represents a venue."""

    location: Location
    title: str
    address: str
    foursquare_id: Optional[str] = None
    foursquare_type: Optional[str] = None
    google_place_id: Optional[str] = None
    google_place_type: Optional[str] = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False, compare=False)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Venue":
        return cls(
            location=Location.from_dict(d["location"]) if "location" in d else None,
            title=d.get("title"),
            address=d.get("address"),
            foursquare_id=d.get("foursquare_id"),
            foursquare_type=d.get("foursquare_type"),
            google_place_id=d.get("google_place_id"),
            google_place_type=d.get("google_place_type"),
            raw=d,
        )


@dataclass(slots=True)
class Video:
    """This object represents a video file."""

    file_id: str
    file_unique_id: str
    width: int
    height: int
    duration: int
    thumbnail: Optional[PhotoSize] = None
    cover: Optional[list[PhotoSize]] = None
    start_timestamp: Optional[int] = None
    qualities: Optional[list[dict[str, Any]]] = None
    file_name: Optional[str] = None
    mime_type: Optional[str] = None
    file_size: Optional[int] = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False, compare=False)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Video":
        return cls(
            file_id=d.get("file_id"),
            file_unique_id=d.get("file_unique_id"),
            width=d.get("width"),
            height=d.get("height"),
            duration=d.get("duration"),
            thumbnail=PhotoSize.from_dict(d["thumbnail"]) if "thumbnail" in d else None,
            cover=[PhotoSize.from_dict(i) for i in d["cover"]] if "cover" in d else None,
            start_timestamp=d.get("start_timestamp"),
            qualities=d.get("qualities"),
            file_name=d.get("file_name"),
            mime_type=d.get("mime_type"),
            file_size=d.get("file_size"),
            raw=d,
        )


@dataclass(slots=True)
class VideoNote:
    """This object represents a video message (available in Telegram apps as of
    v.4.0).
    """

    file_id: str
    file_unique_id: str
    length: int
    duration: int
    thumbnail: Optional[PhotoSize] = None
    file_size: Optional[int] = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False, compare=False)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "VideoNote":
        return cls(
            file_id=d.get("file_id"),
            file_unique_id=d.get("file_unique_id"),
            length=d.get("length"),
            duration=d.get("duration"),
            thumbnail=PhotoSize.from_dict(d["thumbnail"]) if "thumbnail" in d else None,
            file_size=d.get("file_size"),
            raw=d,
        )


@dataclass(slots=True)
class Voice:
    """This object represents a voice note."""

    file_id: str
    file_unique_id: str
    duration: int
    mime_type: Optional[str] = None
    file_size: Optional[int] = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False, compare=False)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Voice":
        return cls(
            file_id=d.get("file_id"),
            file_unique_id=d.get("file_unique_id"),
            duration=d.get("duration"),
            mime_type=d.get("mime_type"),
            file_size=d.get("file_size"),
            raw=d,
        )
