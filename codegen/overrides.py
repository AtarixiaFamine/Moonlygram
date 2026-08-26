"""Hand-maintained configuration for the type generator.

gen_types.py reads the Telegram Bot API spec and emits data-only received
types. This module is where human judgement lives: which types the generator
owns, which it must leave to the hand-written behavior/sent layer, and the
handful of per-field exceptions the spec alone cannot express.

Editing the library's modelled surface means editing the sets below and
re-running ``python codegen/gen_types.py`` — not hand-writing a dataclass.
"""
from __future__ import annotations

# Types the generator OWNS. It emits a dataclass + from_dict for each. Add a
# name here (and re-run the generator) to model a new received type. Order is
# irrelevant; from_dict resolves nested types at call time.
GENERATE: set[str] = {
    # media / files
    "PhotoSize",
    "Document",
    "Audio",
    "Video",
    "Animation",
    "Voice",
    "VideoNote",
    "File",
    "Sticker",
    "StickerSet",
    "LivePhoto",
    # content objects
    "Location",
    "Contact",
    "Venue",
    "Dice",
    "MessageEntity",
    "PollOption",
    "Poll",
    "PollAnswer",
    # chat membership / invites / boosts
    "ChatMemberUpdated",
    "ChatInviteLink",
    "ChatBoost",
    "UserChatBoosts",
    "ChatBoostUpdated",
    "ChatBoostRemoved",
    # reactions
    "ReactionCount",
    "MessageReactionUpdated",
    "MessageReactionCountUpdated",
    # misc small results
    "MessageId",
    "SentWebAppMessage",
    "BotName",
    "BotDescription",
    "BotShortDescription",
    "ForumTopic",
    "UserProfilePhotos",
    # payments
    "Invoice",
    "SuccessfulPayment",
    "RefundedPayment",
    "OrderInfo",
    "ShippingAddress",
    # stars
    "StarTransactions",
    "StarTransaction",
    "StarAmount",
    "AffiliateInfo",
    # communities
    "Community",
    "CommunityChatAdded",
    "CommunityChatJoined",
    "CommunityChatRemoved",
    # unique gifts (the received side; the gift methods stay unimplemented)
    "UniqueGiftInfo",
    "UniqueGift",
    "UniqueGiftModel",
    "UniqueGiftSymbol",
    "UniqueGiftBackdrop",
    "UniqueGiftBackdropColors",
    "UniqueGiftColors",
    # received rich messages (the send side is hand-written in rich/blocks.py)
    "RichMessage",
    "RichBlockListItem",
    # subscriptions and generation updates
    "BotSubscriptionUpdated",
    "MessageGenerationStopped",
}

# Abstract spec types modelled as a single FLAT dataclass: the union of every
# concrete subtype's field, with the discriminator (type / status / source) and
# any field common+required across all subtypes kept required and the rest
# optional. Variant-specific extras still land in `raw`. Mirrors the original
# hand-written MessageOrigin / ChatMember / ChatBoostSource.
FLAT_UNIONS: set[str] = {
    "RichText",
    "RichBlock",
    "MessageOrigin",
    "ChatMember",
    "ChatBoostSource",
    "TransactionPartner",
    "RevenueWithdrawalState",
}

# Behavior-bearing types that stay HAND-WRITTEN in types.py (async shortcut
# methods + recursive set_bot binding). The generator never emits these, but it
# MAY reference them: a generated field typed as one of these is parsed with
# `<Name>.from_dict(...)`. Keep in sync with the classes defined in types.py.
BEHAVIOR_TYPES: set[str] = {
    "User",
    "Chat",
    "Message",
    "CallbackQuery",
    "InlineQuery",
    "ChosenInlineResult",
    "ChatJoinRequest",
    "ShippingQuery",
    "PreCheckoutQuery",
}

# Other types the generator may reference by `.from_dict` but does not own here
# (hand-written received types it should treat as parseable rather than raw).
# These stay hand-written because they are also SENT (carry a to_dict).
HANDWRITTEN_PARSEABLE: set[str] = {
    "ChatPermissions",
    "ChatAdministratorRights",
    "MaskPosition",
    # shared by both directions: the spec has no Input* counterpart for these
    "RichBlockCaption",
    "RichBlockTableCell",
    "RichMessageButton",
}

# Generated types that types.py re-exports under a different name, because the
# spec name is already taken by the send-side API. The generator still emits the
# spec name; only the alias is public.
RENAMED_IN_TYPES: dict[str, str] = {
    # RichMessage is the send-side builder, the library's headline API.
    "RichMessage": "RichMessageContent",
    # RichText is the loose alias a caller passes when sending.
    "RichText": "RichTextNode",
}

# Per-(type, field) annotation overrides, e.g. polymorphic file inputs or union
# aliases the spec expresses loosely. Value is the literal Python annotation.
FIELD_TYPE_OVERRIDES: dict[tuple[str, str], str] = {
    # ReactionType is a hand-written Union parsed by helpers, not a dataclass.
    ("ReactionCount", "type"): '"ReactionType"',
    ("MessageReactionUpdated", "old_reaction"): '"list[ReactionType]"',
    ("MessageReactionUpdated", "new_reaction"): '"list[ReactionType]"',
    # RichText is a string, a list, or a node object, so the alias covers all
    # three rather than naming the dataclass.
    ("RichText", "text"): '"RichTextValue"',
    ("RichBlock", "text"): '"RichTextValue"',
    ("RichBlock", "credit"): '"RichTextValue"',
    ("RichBlock", "summary"): '"RichTextValue"',
    # A media block captions with RichBlockCaption, a table with RichText.
    ("RichBlock", "caption"): '"RichBlockCaption | RichTextValue"',
}

# Per-(type, field) PARSE-EXPRESSION overrides for from_dict. `{d}` is the
# source dict and `{k}` the API key. Used for fields handled by a bespoke helper
# (e.g. ReactionType via _reactions) rather than a plain .from_dict.
FIELD_PARSE_OVERRIDES: dict[tuple[str, str], str] = {
    ("ReactionCount", "type"): '_reaction_type({d}.get("{k}", {{}}))',
    ("MessageReactionUpdated", "old_reaction"): '_reactions({d}.get("{k}"))',
    ("MessageReactionUpdated", "new_reaction"): '_reactions({d}.get("{k}"))',
    ("RichText", "text"): '_rich_text({d}.get("{k}"))',
    ("RichBlock", "text"): '_rich_text({d}.get("{k}"))',
    ("RichBlock", "credit"): '_rich_text({d}.get("{k}"))',
    ("RichBlock", "summary"): '_rich_text({d}.get("{k}"))',
    ("RichBlock", "caption"): '_rich_caption({d}.get("{k}"))',
}

# Names imported into the generated module from .types (helpers/behavior types
# its parse code references at runtime). The generator already imports the
# behavior/handwritten types a field references; list here only the extras a
# parse/type override needs (e.g. the ReactionType helpers).
EXTRA_IMPORTS_FROM_TYPES: set[str] = {
    "ReactionType",
    "_reaction_type",
    "_reactions",
    "RichTextValue",
    "_rich_text",
    "_rich_caption",
}
