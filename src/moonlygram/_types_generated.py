"""Generated Bot API data types — do not edit by hand.

Produced by codegen/gen_types.py from Bot API 10.3.
Edit codegen/overrides.py and re-run the generator instead.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from .types import (  # noqa: E402
    Chat as Chat,
    MaskPosition as MaskPosition,
    ReactionType as ReactionType,
    RichBlockCaption as RichBlockCaption,
    RichBlockTableCell as RichBlockTableCell,
    RichMessageButton as RichMessageButton,
    RichTextValue as RichTextValue,
    User as User,
    _reaction_type as _reaction_type,
    _reactions as _reactions,
    _rich_caption as _rich_caption,
    _rich_text as _rich_text,
)


@dataclass(slots=True)
class AffiliateInfo:
    """Contains information about the affiliate that received a commission via this
    transaction.
    """

    commission_per_mille: int
    amount: int
    affiliate_user: Optional[User] = None
    affiliate_chat: Optional[Chat] = None
    nanostar_amount: Optional[int] = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False, compare=False)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "AffiliateInfo":
        return cls(
            commission_per_mille=d.get("commission_per_mille"),
            amount=d.get("amount"),
            affiliate_user=User.from_dict(d["affiliate_user"]) if "affiliate_user" in d else None,
            affiliate_chat=Chat.from_dict(d["affiliate_chat"]) if "affiliate_chat" in d else None,
            nanostar_amount=d.get("nanostar_amount"),
            raw=d,
        )

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "commission_per_mille": self.commission_per_mille,
            "amount": self.amount,
            "affiliate_user": self.affiliate_user,
            "affiliate_chat": self.affiliate_chat,
            "nanostar_amount": self.nanostar_amount,
        }
        return {k: v for k, v in d.items() if v is not None}


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

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "file_id": self.file_id,
            "file_unique_id": self.file_unique_id,
            "width": self.width,
            "height": self.height,
            "duration": self.duration,
            "thumbnail": self.thumbnail,
            "file_name": self.file_name,
            "mime_type": self.mime_type,
            "file_size": self.file_size,
        }
        return {k: v for k, v in d.items() if v is not None}


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

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "file_id": self.file_id,
            "file_unique_id": self.file_unique_id,
            "duration": self.duration,
            "performer": self.performer,
            "title": self.title,
            "file_name": self.file_name,
            "mime_type": self.mime_type,
            "file_size": self.file_size,
            "thumbnail": self.thumbnail,
        }
        return {k: v for k, v in d.items() if v is not None}


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

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "description": self.description,
        }
        return {k: v for k, v in d.items() if v is not None}


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

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "name": self.name,
        }
        return {k: v for k, v in d.items() if v is not None}


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

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "short_description": self.short_description,
        }
        return {k: v for k, v in d.items() if v is not None}


@dataclass(slots=True)
class BotSubscriptionUpdated:
    """This object contains information about changes to a user payment subscription
    toward the current bot.
    """

    user: User
    invoice_payload: str
    state: str
    raw: dict[str, Any] = field(default_factory=dict, repr=False, compare=False)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "BotSubscriptionUpdated":
        return cls(
            user=User.from_dict(d["user"]) if "user" in d else None,
            invoice_payload=d.get("invoice_payload"),
            state=d.get("state"),
            raw=d,
        )

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "user": self.user,
            "invoice_payload": self.invoice_payload,
            "state": self.state,
        }
        return {k: v for k, v in d.items() if v is not None}


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

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "boost_id": self.boost_id,
            "add_date": self.add_date,
            "expiration_date": self.expiration_date,
            "source": self.source,
        }
        return {k: v for k, v in d.items() if v is not None}


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

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "chat": self.chat,
            "boost_id": self.boost_id,
            "remove_date": self.remove_date,
            "source": self.source,
        }
        return {k: v for k, v in d.items() if v is not None}


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

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "source": self.source,
            "user": self.user,
            "giveaway_message_id": self.giveaway_message_id,
            "prize_star_count": self.prize_star_count,
            "is_unclaimed": self.is_unclaimed,
        }
        return {k: v for k, v in d.items() if v is not None}


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

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "chat": self.chat,
            "boost": self.boost,
        }
        return {k: v for k, v in d.items() if v is not None}


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

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "invite_link": self.invite_link,
            "creator": self.creator,
            "creates_join_request": self.creates_join_request,
            "is_primary": self.is_primary,
            "is_revoked": self.is_revoked,
            "name": self.name,
            "expire_date": self.expire_date,
            "member_limit": self.member_limit,
            "pending_join_request_count": self.pending_join_request_count,
            "subscription_period": self.subscription_period,
            "subscription_price": self.subscription_price,
        }
        return {k: v for k, v in d.items() if v is not None}


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
    can_send_welcome_messages: Optional[bool] = None
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
            can_send_welcome_messages=d.get("can_send_welcome_messages"),
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

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "status": self.status,
            "user": self.user,
            "is_anonymous": self.is_anonymous,
            "custom_title": self.custom_title,
            "can_be_edited": self.can_be_edited,
            "can_manage_chat": self.can_manage_chat,
            "can_delete_messages": self.can_delete_messages,
            "can_manage_video_chats": self.can_manage_video_chats,
            "can_restrict_members": self.can_restrict_members,
            "can_promote_members": self.can_promote_members,
            "can_change_info": self.can_change_info,
            "can_invite_users": self.can_invite_users,
            "can_post_stories": self.can_post_stories,
            "can_edit_stories": self.can_edit_stories,
            "can_delete_stories": self.can_delete_stories,
            "can_post_messages": self.can_post_messages,
            "can_edit_messages": self.can_edit_messages,
            "can_pin_messages": self.can_pin_messages,
            "can_manage_topics": self.can_manage_topics,
            "can_manage_direct_messages": self.can_manage_direct_messages,
            "can_manage_tags": self.can_manage_tags,
            "can_send_welcome_messages": self.can_send_welcome_messages,
            "tag": self.tag,
            "until_date": self.until_date,
            "is_member": self.is_member,
            "can_send_messages": self.can_send_messages,
            "can_send_audios": self.can_send_audios,
            "can_send_documents": self.can_send_documents,
            "can_send_photos": self.can_send_photos,
            "can_send_videos": self.can_send_videos,
            "can_send_video_notes": self.can_send_video_notes,
            "can_send_voice_notes": self.can_send_voice_notes,
            "can_send_polls": self.can_send_polls,
            "can_send_other_messages": self.can_send_other_messages,
            "can_add_web_page_previews": self.can_add_web_page_previews,
            "can_react_to_messages": self.can_react_to_messages,
            "can_edit_tag": self.can_edit_tag,
        }
        return {k: v for k, v in d.items() if v is not None}


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

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "chat": self.chat,
            "from": self.from_user,
            "date": self.date,
            "old_chat_member": self.old_chat_member,
            "new_chat_member": self.new_chat_member,
            "invite_link": self.invite_link,
            "via_join_request": self.via_join_request,
            "via_chat_folder_invite_link": self.via_chat_folder_invite_link,
        }
        return {k: v for k, v in d.items() if v is not None}


@dataclass(slots=True)
class Community:
    """Represents a community (a group of chats)."""

    id: int
    name: str
    raw: dict[str, Any] = field(default_factory=dict, repr=False, compare=False)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Community":
        return cls(
            id=d.get("id"),
            name=d.get("name"),
            raw=d,
        )

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "id": self.id,
            "name": self.name,
        }
        return {k: v for k, v in d.items() if v is not None}


@dataclass(slots=True)
class CommunityChatAdded:
    """Describes a service message about a chat or a bot being added to a community."""

    community: Community
    raw: dict[str, Any] = field(default_factory=dict, repr=False, compare=False)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "CommunityChatAdded":
        return cls(
            community=Community.from_dict(d["community"]) if "community" in d else None,
            raw=d,
        )

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "community": self.community,
        }
        return {k: v for k, v in d.items() if v is not None}


@dataclass(slots=True)
class CommunityChatJoined:
    """Describes a service message about a chat being joined by a user from a
    community.
    """

    community: Community
    raw: dict[str, Any] = field(default_factory=dict, repr=False, compare=False)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "CommunityChatJoined":
        return cls(
            community=Community.from_dict(d["community"]) if "community" in d else None,
            raw=d,
        )

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "community": self.community,
        }
        return {k: v for k, v in d.items() if v is not None}


@dataclass(slots=True)
class CommunityChatRemoved:
    """Describes a service message about a chat or a bot being removed from a
    community. Currently holds no information.
    """

    raw: dict[str, Any] = field(default_factory=dict, repr=False, compare=False)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "CommunityChatRemoved":
        return cls(
            raw=d,
        )

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
        }
        return {k: v for k, v in d.items() if v is not None}


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

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "phone_number": self.phone_number,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "user_id": self.user_id,
            "vcard": self.vcard,
        }
        return {k: v for k, v in d.items() if v is not None}


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

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "emoji": self.emoji,
            "value": self.value,
        }
        return {k: v for k, v in d.items() if v is not None}


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

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "file_id": self.file_id,
            "file_unique_id": self.file_unique_id,
            "thumbnail": self.thumbnail,
            "file_name": self.file_name,
            "mime_type": self.mime_type,
            "file_size": self.file_size,
        }
        return {k: v for k, v in d.items() if v is not None}


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

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "file_id": self.file_id,
            "file_unique_id": self.file_unique_id,
            "file_size": self.file_size,
            "file_path": self.file_path,
        }
        return {k: v for k, v in d.items() if v is not None}


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

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "message_thread_id": self.message_thread_id,
            "name": self.name,
            "icon_color": self.icon_color,
            "icon_custom_emoji_id": self.icon_custom_emoji_id,
            "is_name_implicit": self.is_name_implicit,
        }
        return {k: v for k, v in d.items() if v is not None}


@dataclass(slots=True)
class Invoice:
    """This object contains basic information about an invoice."""

    title: str
    description: str
    start_parameter: str
    currency: str
    total_amount: int
    raw: dict[str, Any] = field(default_factory=dict, repr=False, compare=False)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Invoice":
        return cls(
            title=d.get("title"),
            description=d.get("description"),
            start_parameter=d.get("start_parameter"),
            currency=d.get("currency"),
            total_amount=d.get("total_amount"),
            raw=d,
        )

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "title": self.title,
            "description": self.description,
            "start_parameter": self.start_parameter,
            "currency": self.currency,
            "total_amount": self.total_amount,
        }
        return {k: v for k, v in d.items() if v is not None}


@dataclass(slots=True)
class LivePhoto:
    """This object represents a live photo."""

    file_id: str
    file_unique_id: str
    width: int
    height: int
    duration: int
    photo: Optional[list[PhotoSize]] = None
    mime_type: Optional[str] = None
    file_size: Optional[int] = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False, compare=False)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "LivePhoto":
        return cls(
            file_id=d.get("file_id"),
            file_unique_id=d.get("file_unique_id"),
            width=d.get("width"),
            height=d.get("height"),
            duration=d.get("duration"),
            photo=[PhotoSize.from_dict(i) for i in d["photo"]] if "photo" in d else None,
            mime_type=d.get("mime_type"),
            file_size=d.get("file_size"),
            raw=d,
        )

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "file_id": self.file_id,
            "file_unique_id": self.file_unique_id,
            "width": self.width,
            "height": self.height,
            "duration": self.duration,
            "photo": self.photo,
            "mime_type": self.mime_type,
            "file_size": self.file_size,
        }
        return {k: v for k, v in d.items() if v is not None}


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

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "horizontal_accuracy": self.horizontal_accuracy,
            "live_period": self.live_period,
            "heading": self.heading,
            "proximity_alert_radius": self.proximity_alert_radius,
        }
        return {k: v for k, v in d.items() if v is not None}


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

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "type": self.type,
            "offset": self.offset,
            "length": self.length,
            "url": self.url,
            "user": self.user,
            "language": self.language,
            "custom_emoji_id": self.custom_emoji_id,
            "unix_time": self.unix_time,
            "date_time_format": self.date_time_format,
        }
        return {k: v for k, v in d.items() if v is not None}


@dataclass(slots=True)
class MessageGenerationStopped:
    """This object describes an update about a user stopping message generation."""

    chat: Chat
    draft_id: int
    message_thread_id: Optional[int] = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False, compare=False)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "MessageGenerationStopped":
        return cls(
            chat=Chat.from_dict(d["chat"]) if "chat" in d else None,
            draft_id=d.get("draft_id"),
            message_thread_id=d.get("message_thread_id"),
            raw=d,
        )

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "chat": self.chat,
            "draft_id": self.draft_id,
            "message_thread_id": self.message_thread_id,
        }
        return {k: v for k, v in d.items() if v is not None}


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

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "message_id": self.message_id,
        }
        return {k: v for k, v in d.items() if v is not None}


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

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "type": self.type,
            "date": self.date,
            "sender_user": self.sender_user,
            "sender_user_name": self.sender_user_name,
            "sender_chat": self.sender_chat,
            "author_signature": self.author_signature,
            "chat": self.chat,
            "message_id": self.message_id,
        }
        return {k: v for k, v in d.items() if v is not None}


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

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "chat": self.chat,
            "message_id": self.message_id,
            "date": self.date,
            "reactions": self.reactions,
        }
        return {k: v for k, v in d.items() if v is not None}


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

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "chat": self.chat,
            "message_id": self.message_id,
            "date": self.date,
            "old_reaction": self.old_reaction,
            "new_reaction": self.new_reaction,
            "user": self.user,
            "actor_chat": self.actor_chat,
        }
        return {k: v for k, v in d.items() if v is not None}


@dataclass(slots=True)
class OrderInfo:
    """This object represents information about an order."""

    name: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    shipping_address: Optional[ShippingAddress] = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False, compare=False)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "OrderInfo":
        return cls(
            name=d.get("name"),
            phone_number=d.get("phone_number"),
            email=d.get("email"),
            shipping_address=ShippingAddress.from_dict(d["shipping_address"]) if "shipping_address" in d else None,
            raw=d,
        )

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "name": self.name,
            "phone_number": self.phone_number,
            "email": self.email,
            "shipping_address": self.shipping_address,
        }
        return {k: v for k, v in d.items() if v is not None}


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

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "file_id": self.file_id,
            "file_unique_id": self.file_unique_id,
            "width": self.width,
            "height": self.height,
            "file_size": self.file_size,
        }
        return {k: v for k, v in d.items() if v is not None}


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

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "id": self.id,
            "question": self.question,
            "options": self.options,
            "total_voter_count": self.total_voter_count,
            "is_closed": self.is_closed,
            "is_anonymous": self.is_anonymous,
            "type": self.type,
            "allows_multiple_answers": self.allows_multiple_answers,
            "allows_revoting": self.allows_revoting,
            "members_only": self.members_only,
            "question_entities": self.question_entities,
            "country_codes": self.country_codes,
            "correct_option_ids": self.correct_option_ids,
            "explanation": self.explanation,
            "explanation_entities": self.explanation_entities,
            "explanation_media": self.explanation_media,
            "open_period": self.open_period,
            "close_date": self.close_date,
            "description": self.description,
            "description_entities": self.description_entities,
            "media": self.media,
        }
        return {k: v for k, v in d.items() if v is not None}


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

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "poll_id": self.poll_id,
            "option_ids": self.option_ids,
            "option_persistent_ids": self.option_persistent_ids,
            "voter_chat": self.voter_chat,
            "user": self.user,
        }
        return {k: v for k, v in d.items() if v is not None}


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

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "persistent_id": self.persistent_id,
            "text": self.text,
            "voter_count": self.voter_count,
            "text_entities": self.text_entities,
            "media": self.media,
            "added_by_user": self.added_by_user,
            "added_by_chat": self.added_by_chat,
            "addition_date": self.addition_date,
        }
        return {k: v for k, v in d.items() if v is not None}


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

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "type": self.type,
            "total_count": self.total_count,
        }
        return {k: v for k, v in d.items() if v is not None}


@dataclass(slots=True)
class RefundedPayment:
    """This object contains basic information about a refunded payment."""

    currency: str
    total_amount: int
    invoice_payload: str
    telegram_payment_charge_id: str
    provider_payment_charge_id: Optional[str] = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False, compare=False)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "RefundedPayment":
        return cls(
            currency=d.get("currency"),
            total_amount=d.get("total_amount"),
            invoice_payload=d.get("invoice_payload"),
            telegram_payment_charge_id=d.get("telegram_payment_charge_id"),
            provider_payment_charge_id=d.get("provider_payment_charge_id"),
            raw=d,
        )

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "currency": self.currency,
            "total_amount": self.total_amount,
            "invoice_payload": self.invoice_payload,
            "telegram_payment_charge_id": self.telegram_payment_charge_id,
            "provider_payment_charge_id": self.provider_payment_charge_id,
        }
        return {k: v for k, v in d.items() if v is not None}


@dataclass(slots=True)
class RevenueWithdrawalState:
    """This object describes the state of a revenue withdrawal operation. Currently,
    it can be one of - RevenueWithdrawalStatePending -
    RevenueWithdrawalStateSucceeded - RevenueWithdrawalStateFailed
    """

    type: str
    date: Optional[int] = None
    url: Optional[str] = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False, compare=False)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "RevenueWithdrawalState":
        return cls(
            type=d.get("type"),
            date=d.get("date"),
            url=d.get("url"),
            raw=d,
        )

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "type": self.type,
            "date": self.date,
            "url": self.url,
        }
        return {k: v for k, v in d.items() if v is not None}


@dataclass(slots=True)
class RichBlock:
    """This object represents a block in a rich formatted message. Currently, it can
    be any of the following types: - RichBlockParagraph - RichBlockSectionHeading -
    RichBlockPreformatted - RichBlockFooter - RichBlockDivider -
    RichBlockMathematicalExpression - RichBlockAnchor - RichBlockList -
    RichBlockBlockQuotation - RichBlockExpandableBlockQuotation -
    RichBlockPullQuotation - RichBlockCollage - RichBlockSlideshow - RichBlockTable
    - RichBlockDetails - RichBlockMap - RichBlockButtons - RichBlockAnimation -
    RichBlockAudio - RichBlockDocument - RichBlockPhoto - RichBlockVideo -
    RichBlockVoiceNote - RichBlockThinking
    """

    type: str
    text: Optional[RichTextValue] = None
    size: Optional[int] = None
    language: Optional[str] = None
    expression: Optional[str] = None
    name: Optional[str] = None
    items: Optional[list[RichBlockListItem]] = None
    blocks: Optional[list[RichBlock]] = None
    credit: Optional[RichTextValue] = None
    caption: Optional[RichBlockCaption | RichTextValue] = None
    cells: Optional[list[list[RichBlockTableCell]]] = None
    is_bordered: Optional[bool] = None
    is_striped: Optional[bool] = None
    is_compact: Optional[bool] = None
    summary: Optional[RichTextValue] = None
    is_open: Optional[bool] = None
    location: Optional[Location] = None
    zoom: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    buttons: Optional[list[RichMessageButton]] = None
    align: Optional[str] = None
    animation: Optional[Animation] = None
    has_spoiler: Optional[bool] = None
    audio: Optional[Audio] = None
    document: Optional[Document] = None
    photo: Optional[list[PhotoSize]] = None
    video: Optional[Video] = None
    voice_note: Optional[Voice] = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False, compare=False)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "RichBlock":
        return cls(
            type=d.get("type"),
            text=_rich_text(d.get("text")),
            size=d.get("size"),
            language=d.get("language"),
            expression=d.get("expression"),
            name=d.get("name"),
            items=[RichBlockListItem.from_dict(i) for i in d["items"]] if "items" in d else None,
            blocks=[RichBlock.from_dict(i) for i in d["blocks"]] if "blocks" in d else None,
            credit=_rich_text(d.get("credit")),
            caption=_rich_caption(d.get("caption")),
            cells=[[RichBlockTableCell.from_dict(j) for j in i] for i in d["cells"]] if "cells" in d else None,
            is_bordered=d.get("is_bordered"),
            is_striped=d.get("is_striped"),
            is_compact=d.get("is_compact"),
            summary=_rich_text(d.get("summary")),
            is_open=d.get("is_open"),
            location=Location.from_dict(d["location"]) if "location" in d else None,
            zoom=d.get("zoom"),
            width=d.get("width"),
            height=d.get("height"),
            buttons=[RichMessageButton.from_dict(i) for i in d["buttons"]] if "buttons" in d else None,
            align=d.get("align"),
            animation=Animation.from_dict(d["animation"]) if "animation" in d else None,
            has_spoiler=d.get("has_spoiler"),
            audio=Audio.from_dict(d["audio"]) if "audio" in d else None,
            document=Document.from_dict(d["document"]) if "document" in d else None,
            photo=[PhotoSize.from_dict(i) for i in d["photo"]] if "photo" in d else None,
            video=Video.from_dict(d["video"]) if "video" in d else None,
            voice_note=Voice.from_dict(d["voice_note"]) if "voice_note" in d else None,
            raw=d,
        )

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "type": self.type,
            "text": self.text,
            "size": self.size,
            "language": self.language,
            "expression": self.expression,
            "name": self.name,
            "items": self.items,
            "blocks": self.blocks,
            "credit": self.credit,
            "caption": self.caption,
            "cells": self.cells,
            "is_bordered": self.is_bordered,
            "is_striped": self.is_striped,
            "is_compact": self.is_compact,
            "summary": self.summary,
            "is_open": self.is_open,
            "location": self.location,
            "zoom": self.zoom,
            "width": self.width,
            "height": self.height,
            "buttons": self.buttons,
            "align": self.align,
            "animation": self.animation,
            "has_spoiler": self.has_spoiler,
            "audio": self.audio,
            "document": self.document,
            "photo": self.photo,
            "video": self.video,
            "voice_note": self.voice_note,
        }
        return {k: v for k, v in d.items() if v is not None}


@dataclass(slots=True)
class RichBlockListItem:
    """An item of a list."""

    label: str
    blocks: list[RichBlock]
    has_checkbox: Optional[bool] = None
    is_checked: Optional[bool] = None
    value: Optional[int] = None
    type: Optional[str] = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False, compare=False)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "RichBlockListItem":
        return cls(
            label=d.get("label"),
            blocks=[RichBlock.from_dict(i) for i in d["blocks"]] if "blocks" in d else None,
            has_checkbox=d.get("has_checkbox"),
            is_checked=d.get("is_checked"),
            value=d.get("value"),
            type=d.get("type"),
            raw=d,
        )

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "label": self.label,
            "blocks": self.blocks,
            "has_checkbox": self.has_checkbox,
            "is_checked": self.is_checked,
            "value": self.value,
            "type": self.type,
        }
        return {k: v for k, v in d.items() if v is not None}


@dataclass(slots=True)
class RichMessage:
    """Rich formatted message."""

    blocks: list[RichBlock]
    is_rtl: Optional[bool] = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False, compare=False)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "RichMessage":
        return cls(
            blocks=[RichBlock.from_dict(i) for i in d["blocks"]] if "blocks" in d else None,
            is_rtl=d.get("is_rtl"),
            raw=d,
        )

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "blocks": self.blocks,
            "is_rtl": self.is_rtl,
        }
        return {k: v for k, v in d.items() if v is not None}


@dataclass(slots=True)
class RichText:
    """This object represents a rich formatted text. Currently, it can be either a
    String for plain text, an Array of RichText, or any of the following types: -
    RichTextBold - RichTextItalic - RichTextUnderline - RichTextStrikethrough -
    RichTextSpoiler - RichTextDateTime - RichTextTextMention - RichTextSubscript -
    RichTextSuperscript - RichTextMarked - RichTextCode - RichTextCustomEmoji -
    RichTextMathematicalExpression - RichTextUrl - RichTextEmailAddress -
    RichTextPhoneNumber - RichTextBankCardNumber - RichTextMention -
    RichTextHashtag - RichTextCashtag - RichTextBotCommand - RichTextButton -
    RichTextAnchor - RichTextAnchorLink - RichTextReference - RichTextReferenceLink
    """

    type: str
    text: Optional[RichTextValue] = None
    unix_time: Optional[int] = None
    date_time_format: Optional[str] = None
    user: Optional[User] = None
    custom_emoji_id: Optional[str] = None
    alternative_text: Optional[str] = None
    expression: Optional[str] = None
    url: Optional[str] = None
    email_address: Optional[str] = None
    phone_number: Optional[str] = None
    bank_card_number: Optional[str] = None
    username: Optional[str] = None
    hashtag: Optional[str] = None
    cashtag: Optional[str] = None
    bot_command: Optional[str] = None
    button: Optional[RichMessageButton] = None
    name: Optional[str] = None
    anchor_name: Optional[str] = None
    reference_name: Optional[str] = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False, compare=False)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "RichText":
        return cls(
            type=d.get("type"),
            text=_rich_text(d.get("text")),
            unix_time=d.get("unix_time"),
            date_time_format=d.get("date_time_format"),
            user=User.from_dict(d["user"]) if "user" in d else None,
            custom_emoji_id=d.get("custom_emoji_id"),
            alternative_text=d.get("alternative_text"),
            expression=d.get("expression"),
            url=d.get("url"),
            email_address=d.get("email_address"),
            phone_number=d.get("phone_number"),
            bank_card_number=d.get("bank_card_number"),
            username=d.get("username"),
            hashtag=d.get("hashtag"),
            cashtag=d.get("cashtag"),
            bot_command=d.get("bot_command"),
            button=RichMessageButton.from_dict(d["button"]) if "button" in d else None,
            name=d.get("name"),
            anchor_name=d.get("anchor_name"),
            reference_name=d.get("reference_name"),
            raw=d,
        )

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "type": self.type,
            "text": self.text,
            "unix_time": self.unix_time,
            "date_time_format": self.date_time_format,
            "user": self.user,
            "custom_emoji_id": self.custom_emoji_id,
            "alternative_text": self.alternative_text,
            "expression": self.expression,
            "url": self.url,
            "email_address": self.email_address,
            "phone_number": self.phone_number,
            "bank_card_number": self.bank_card_number,
            "username": self.username,
            "hashtag": self.hashtag,
            "cashtag": self.cashtag,
            "bot_command": self.bot_command,
            "button": self.button,
            "name": self.name,
            "anchor_name": self.anchor_name,
            "reference_name": self.reference_name,
        }
        return {k: v for k, v in d.items() if v is not None}


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

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "inline_message_id": self.inline_message_id,
        }
        return {k: v for k, v in d.items() if v is not None}


@dataclass(slots=True)
class ShippingAddress:
    """This object represents a shipping address."""

    country_code: str
    state: str
    city: str
    street_line1: str
    street_line2: str
    post_code: str
    raw: dict[str, Any] = field(default_factory=dict, repr=False, compare=False)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "ShippingAddress":
        return cls(
            country_code=d.get("country_code"),
            state=d.get("state"),
            city=d.get("city"),
            street_line1=d.get("street_line1"),
            street_line2=d.get("street_line2"),
            post_code=d.get("post_code"),
            raw=d,
        )

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "country_code": self.country_code,
            "state": self.state,
            "city": self.city,
            "street_line1": self.street_line1,
            "street_line2": self.street_line2,
            "post_code": self.post_code,
        }
        return {k: v for k, v in d.items() if v is not None}


@dataclass(slots=True)
class StarAmount:
    """Describes an amount of Telegram Stars."""

    amount: int
    nanostar_amount: Optional[int] = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False, compare=False)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "StarAmount":
        return cls(
            amount=d.get("amount"),
            nanostar_amount=d.get("nanostar_amount"),
            raw=d,
        )

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "amount": self.amount,
            "nanostar_amount": self.nanostar_amount,
        }
        return {k: v for k, v in d.items() if v is not None}


@dataclass(slots=True)
class StarTransaction:
    """Describes a Telegram Star transaction. Note that if the buyer initiates a
    chargeback with the payment provider from whom they acquired Stars (e.g.,
    Apple, Google) following this transaction, the refunded Stars will be deducted
    from the bot's balance. This is outside of Telegram's control.
    """

    id: str
    amount: int
    date: int
    nanostar_amount: Optional[int] = None
    source: Optional[TransactionPartner] = None
    receiver: Optional[TransactionPartner] = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False, compare=False)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "StarTransaction":
        return cls(
            id=d.get("id"),
            amount=d.get("amount"),
            date=d.get("date"),
            nanostar_amount=d.get("nanostar_amount"),
            source=TransactionPartner.from_dict(d["source"]) if "source" in d else None,
            receiver=TransactionPartner.from_dict(d["receiver"]) if "receiver" in d else None,
            raw=d,
        )

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "id": self.id,
            "amount": self.amount,
            "date": self.date,
            "nanostar_amount": self.nanostar_amount,
            "source": self.source,
            "receiver": self.receiver,
        }
        return {k: v for k, v in d.items() if v is not None}


@dataclass(slots=True)
class StarTransactions:
    """Contains a list of Telegram Star transactions."""

    transactions: list[StarTransaction]
    raw: dict[str, Any] = field(default_factory=dict, repr=False, compare=False)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "StarTransactions":
        return cls(
            transactions=[StarTransaction.from_dict(i) for i in d["transactions"]] if "transactions" in d else None,
            raw=d,
        )

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "transactions": self.transactions,
        }
        return {k: v for k, v in d.items() if v is not None}


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

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "file_id": self.file_id,
            "file_unique_id": self.file_unique_id,
            "type": self.type,
            "width": self.width,
            "height": self.height,
            "is_animated": self.is_animated,
            "is_video": self.is_video,
            "thumbnail": self.thumbnail,
            "emoji": self.emoji,
            "set_name": self.set_name,
            "premium_animation": self.premium_animation,
            "mask_position": self.mask_position,
            "custom_emoji_id": self.custom_emoji_id,
            "needs_repainting": self.needs_repainting,
            "file_size": self.file_size,
        }
        return {k: v for k, v in d.items() if v is not None}


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

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "name": self.name,
            "title": self.title,
            "sticker_type": self.sticker_type,
            "stickers": self.stickers,
            "thumbnail": self.thumbnail,
        }
        return {k: v for k, v in d.items() if v is not None}


@dataclass(slots=True)
class SuccessfulPayment:
    """This object contains basic information about a successful payment. Note that if
    the buyer initiates a chargeback with the relevant payment provider following
    this transaction, the funds may be debited from your balance. This is outside
    of Telegram's control.
    """

    currency: str
    total_amount: int
    invoice_payload: str
    telegram_payment_charge_id: str
    provider_payment_charge_id: str
    subscription_expiration_date: Optional[int] = None
    is_recurring: Optional[bool] = None
    is_first_recurring: Optional[bool] = None
    shipping_option_id: Optional[str] = None
    order_info: Optional[OrderInfo] = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False, compare=False)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "SuccessfulPayment":
        return cls(
            currency=d.get("currency"),
            total_amount=d.get("total_amount"),
            invoice_payload=d.get("invoice_payload"),
            telegram_payment_charge_id=d.get("telegram_payment_charge_id"),
            provider_payment_charge_id=d.get("provider_payment_charge_id"),
            subscription_expiration_date=d.get("subscription_expiration_date"),
            is_recurring=d.get("is_recurring"),
            is_first_recurring=d.get("is_first_recurring"),
            shipping_option_id=d.get("shipping_option_id"),
            order_info=OrderInfo.from_dict(d["order_info"]) if "order_info" in d else None,
            raw=d,
        )

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "currency": self.currency,
            "total_amount": self.total_amount,
            "invoice_payload": self.invoice_payload,
            "telegram_payment_charge_id": self.telegram_payment_charge_id,
            "provider_payment_charge_id": self.provider_payment_charge_id,
            "subscription_expiration_date": self.subscription_expiration_date,
            "is_recurring": self.is_recurring,
            "is_first_recurring": self.is_first_recurring,
            "shipping_option_id": self.shipping_option_id,
            "order_info": self.order_info,
        }
        return {k: v for k, v in d.items() if v is not None}


@dataclass(slots=True)
class TransactionPartner:
    """This object describes the source of a transaction, or its recipient for
    outgoing transactions. Currently, it can be one of - TransactionPartnerUser -
    TransactionPartnerChat - TransactionPartnerAffiliateProgram -
    TransactionPartnerFragment - TransactionPartnerTelegramAds -
    TransactionPartnerTelegramApi - TransactionPartnerOther
    """

    type: str
    transaction_type: Optional[str] = None
    user: Optional[User] = None
    affiliate: Optional[AffiliateInfo] = None
    invoice_payload: Optional[str] = None
    subscription_period: Optional[int] = None
    paid_media: Optional[list[dict[str, Any]]] = None
    paid_media_payload: Optional[str] = None
    gift: Optional[dict[str, Any]] = None
    premium_subscription_duration: Optional[int] = None
    chat: Optional[Chat] = None
    sponsor_user: Optional[User] = None
    commission_per_mille: Optional[int] = None
    withdrawal_state: Optional[RevenueWithdrawalState] = None
    request_count: Optional[int] = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False, compare=False)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "TransactionPartner":
        return cls(
            type=d.get("type"),
            transaction_type=d.get("transaction_type"),
            user=User.from_dict(d["user"]) if "user" in d else None,
            affiliate=AffiliateInfo.from_dict(d["affiliate"]) if "affiliate" in d else None,
            invoice_payload=d.get("invoice_payload"),
            subscription_period=d.get("subscription_period"),
            paid_media=d.get("paid_media"),
            paid_media_payload=d.get("paid_media_payload"),
            gift=d.get("gift"),
            premium_subscription_duration=d.get("premium_subscription_duration"),
            chat=Chat.from_dict(d["chat"]) if "chat" in d else None,
            sponsor_user=User.from_dict(d["sponsor_user"]) if "sponsor_user" in d else None,
            commission_per_mille=d.get("commission_per_mille"),
            withdrawal_state=RevenueWithdrawalState.from_dict(d["withdrawal_state"]) if "withdrawal_state" in d else None,
            request_count=d.get("request_count"),
            raw=d,
        )

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "type": self.type,
            "transaction_type": self.transaction_type,
            "user": self.user,
            "affiliate": self.affiliate,
            "invoice_payload": self.invoice_payload,
            "subscription_period": self.subscription_period,
            "paid_media": self.paid_media,
            "paid_media_payload": self.paid_media_payload,
            "gift": self.gift,
            "premium_subscription_duration": self.premium_subscription_duration,
            "chat": self.chat,
            "sponsor_user": self.sponsor_user,
            "commission_per_mille": self.commission_per_mille,
            "withdrawal_state": self.withdrawal_state,
            "request_count": self.request_count,
        }
        return {k: v for k, v in d.items() if v is not None}


@dataclass(slots=True)
class UniqueGift:
    """This object describes a unique gift that was upgraded from a regular gift."""

    gift_id: str
    base_name: str
    name: str
    number: int
    model: UniqueGiftModel
    symbol: UniqueGiftSymbol
    backdrop: UniqueGiftBackdrop
    is_premium: Optional[bool] = None
    is_burned: Optional[bool] = None
    is_from_blockchain: Optional[bool] = None
    colors: Optional[UniqueGiftColors] = None
    publisher_chat: Optional[Chat] = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False, compare=False)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "UniqueGift":
        return cls(
            gift_id=d.get("gift_id"),
            base_name=d.get("base_name"),
            name=d.get("name"),
            number=d.get("number"),
            model=UniqueGiftModel.from_dict(d["model"]) if "model" in d else None,
            symbol=UniqueGiftSymbol.from_dict(d["symbol"]) if "symbol" in d else None,
            backdrop=UniqueGiftBackdrop.from_dict(d["backdrop"]) if "backdrop" in d else None,
            is_premium=d.get("is_premium"),
            is_burned=d.get("is_burned"),
            is_from_blockchain=d.get("is_from_blockchain"),
            colors=UniqueGiftColors.from_dict(d["colors"]) if "colors" in d else None,
            publisher_chat=Chat.from_dict(d["publisher_chat"]) if "publisher_chat" in d else None,
            raw=d,
        )

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "gift_id": self.gift_id,
            "base_name": self.base_name,
            "name": self.name,
            "number": self.number,
            "model": self.model,
            "symbol": self.symbol,
            "backdrop": self.backdrop,
            "is_premium": self.is_premium,
            "is_burned": self.is_burned,
            "is_from_blockchain": self.is_from_blockchain,
            "colors": self.colors,
            "publisher_chat": self.publisher_chat,
        }
        return {k: v for k, v in d.items() if v is not None}


@dataclass(slots=True)
class UniqueGiftBackdrop:
    """This object describes the backdrop of a unique gift."""

    name: str
    colors: UniqueGiftBackdropColors
    rarity_per_mille: int
    raw: dict[str, Any] = field(default_factory=dict, repr=False, compare=False)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "UniqueGiftBackdrop":
        return cls(
            name=d.get("name"),
            colors=UniqueGiftBackdropColors.from_dict(d["colors"]) if "colors" in d else None,
            rarity_per_mille=d.get("rarity_per_mille"),
            raw=d,
        )

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "name": self.name,
            "colors": self.colors,
            "rarity_per_mille": self.rarity_per_mille,
        }
        return {k: v for k, v in d.items() if v is not None}


@dataclass(slots=True)
class UniqueGiftBackdropColors:
    """This object describes the colors of the backdrop of a unique gift."""

    center_color: int
    edge_color: int
    symbol_color: int
    text_color: int
    raw: dict[str, Any] = field(default_factory=dict, repr=False, compare=False)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "UniqueGiftBackdropColors":
        return cls(
            center_color=d.get("center_color"),
            edge_color=d.get("edge_color"),
            symbol_color=d.get("symbol_color"),
            text_color=d.get("text_color"),
            raw=d,
        )

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "center_color": self.center_color,
            "edge_color": self.edge_color,
            "symbol_color": self.symbol_color,
            "text_color": self.text_color,
        }
        return {k: v for k, v in d.items() if v is not None}


@dataclass(slots=True)
class UniqueGiftColors:
    """This object contains information about the color scheme for a user's name,
    message replies and link previews based on a unique gift.
    """

    model_custom_emoji_id: str
    symbol_custom_emoji_id: str
    light_theme_main_color: int
    light_theme_other_colors: list[int]
    dark_theme_main_color: int
    dark_theme_other_colors: list[int]
    raw: dict[str, Any] = field(default_factory=dict, repr=False, compare=False)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "UniqueGiftColors":
        return cls(
            model_custom_emoji_id=d.get("model_custom_emoji_id"),
            symbol_custom_emoji_id=d.get("symbol_custom_emoji_id"),
            light_theme_main_color=d.get("light_theme_main_color"),
            light_theme_other_colors=d.get("light_theme_other_colors"),
            dark_theme_main_color=d.get("dark_theme_main_color"),
            dark_theme_other_colors=d.get("dark_theme_other_colors"),
            raw=d,
        )

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "model_custom_emoji_id": self.model_custom_emoji_id,
            "symbol_custom_emoji_id": self.symbol_custom_emoji_id,
            "light_theme_main_color": self.light_theme_main_color,
            "light_theme_other_colors": self.light_theme_other_colors,
            "dark_theme_main_color": self.dark_theme_main_color,
            "dark_theme_other_colors": self.dark_theme_other_colors,
        }
        return {k: v for k, v in d.items() if v is not None}


@dataclass(slots=True)
class UniqueGiftInfo:
    """Describes a service message about a unique gift that was sent or received."""

    gift: UniqueGift
    origin: str
    text: Optional[str] = None
    entities: Optional[list[MessageEntity]] = None
    is_private: Optional[bool] = None
    last_resale_currency: Optional[str] = None
    last_resale_amount: Optional[int] = None
    owned_gift_id: Optional[str] = None
    transfer_star_count: Optional[int] = None
    next_transfer_date: Optional[int] = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False, compare=False)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "UniqueGiftInfo":
        return cls(
            gift=UniqueGift.from_dict(d["gift"]) if "gift" in d else None,
            origin=d.get("origin"),
            text=d.get("text"),
            entities=[MessageEntity.from_dict(i) for i in d["entities"]] if "entities" in d else None,
            is_private=d.get("is_private"),
            last_resale_currency=d.get("last_resale_currency"),
            last_resale_amount=d.get("last_resale_amount"),
            owned_gift_id=d.get("owned_gift_id"),
            transfer_star_count=d.get("transfer_star_count"),
            next_transfer_date=d.get("next_transfer_date"),
            raw=d,
        )

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "gift": self.gift,
            "origin": self.origin,
            "text": self.text,
            "entities": self.entities,
            "is_private": self.is_private,
            "last_resale_currency": self.last_resale_currency,
            "last_resale_amount": self.last_resale_amount,
            "owned_gift_id": self.owned_gift_id,
            "transfer_star_count": self.transfer_star_count,
            "next_transfer_date": self.next_transfer_date,
        }
        return {k: v for k, v in d.items() if v is not None}


@dataclass(slots=True)
class UniqueGiftModel:
    """This object describes the model of a unique gift."""

    name: str
    sticker: Sticker
    rarity_per_mille: int
    rarity: Optional[str] = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False, compare=False)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "UniqueGiftModel":
        return cls(
            name=d.get("name"),
            sticker=Sticker.from_dict(d["sticker"]) if "sticker" in d else None,
            rarity_per_mille=d.get("rarity_per_mille"),
            rarity=d.get("rarity"),
            raw=d,
        )

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "name": self.name,
            "sticker": self.sticker,
            "rarity_per_mille": self.rarity_per_mille,
            "rarity": self.rarity,
        }
        return {k: v for k, v in d.items() if v is not None}


@dataclass(slots=True)
class UniqueGiftSymbol:
    """This object describes the symbol shown on the pattern of a unique gift."""

    name: str
    sticker: Sticker
    rarity_per_mille: int
    raw: dict[str, Any] = field(default_factory=dict, repr=False, compare=False)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "UniqueGiftSymbol":
        return cls(
            name=d.get("name"),
            sticker=Sticker.from_dict(d["sticker"]) if "sticker" in d else None,
            rarity_per_mille=d.get("rarity_per_mille"),
            raw=d,
        )

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "name": self.name,
            "sticker": self.sticker,
            "rarity_per_mille": self.rarity_per_mille,
        }
        return {k: v for k, v in d.items() if v is not None}


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

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "boosts": self.boosts,
        }
        return {k: v for k, v in d.items() if v is not None}


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

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "total_count": self.total_count,
            "photos": self.photos,
        }
        return {k: v for k, v in d.items() if v is not None}


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

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "location": self.location,
            "title": self.title,
            "address": self.address,
            "foursquare_id": self.foursquare_id,
            "foursquare_type": self.foursquare_type,
            "google_place_id": self.google_place_id,
            "google_place_type": self.google_place_type,
        }
        return {k: v for k, v in d.items() if v is not None}


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

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "file_id": self.file_id,
            "file_unique_id": self.file_unique_id,
            "width": self.width,
            "height": self.height,
            "duration": self.duration,
            "thumbnail": self.thumbnail,
            "cover": self.cover,
            "start_timestamp": self.start_timestamp,
            "qualities": self.qualities,
            "file_name": self.file_name,
            "mime_type": self.mime_type,
            "file_size": self.file_size,
        }
        return {k: v for k, v in d.items() if v is not None}


@dataclass(slots=True)
class VideoNote:
    """This object represents a video message."""

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

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "file_id": self.file_id,
            "file_unique_id": self.file_unique_id,
            "length": self.length,
            "duration": self.duration,
            "thumbnail": self.thumbnail,
            "file_size": self.file_size,
        }
        return {k: v for k, v in d.items() if v is not None}


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

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "file_id": self.file_id,
            "file_unique_id": self.file_unique_id,
            "duration": self.duration,
            "mime_type": self.mime_type,
            "file_size": self.file_size,
        }
        return {k: v for k, v in d.items() if v is not None}
