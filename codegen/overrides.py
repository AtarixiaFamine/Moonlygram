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
}

# Abstract spec types modelled as a single FLAT dataclass: the union of every
# concrete subtype's field, with the discriminator (type / status / source) and
# any field common+required across all subtypes kept required and the rest
# optional. Variant-specific extras still land in `raw`. Mirrors the original
# hand-written MessageOrigin / ChatMember / ChatBoostSource.
FLAT_UNIONS: set[str] = {
    "MessageOrigin",
    "ChatMember",
    "ChatBoostSource",
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
}

# Other types the generator may reference by `.from_dict` but does not own here
# (hand-written received types it should treat as parseable rather than raw).
# These stay hand-written because they are also SENT (carry a to_dict).
HANDWRITTEN_PARSEABLE: set[str] = {
    "ChatPermissions",
    "ChatAdministratorRights",
    "MaskPosition",
}

# Per-(type, field) annotation overrides, e.g. polymorphic file inputs or union
# aliases the spec expresses loosely. Value is the literal Python annotation.
FIELD_TYPE_OVERRIDES: dict[tuple[str, str], str] = {
    # ReactionType is a hand-written Union parsed by helpers, not a dataclass.
    ("ReactionCount", "type"): '"ReactionType"',
    ("MessageReactionUpdated", "old_reaction"): '"list[ReactionType]"',
    ("MessageReactionUpdated", "new_reaction"): '"list[ReactionType]"',
}

# Per-(type, field) PARSE-EXPRESSION overrides for from_dict. `{d}` is the
# source dict and `{k}` the API key. Used for fields handled by a bespoke helper
# (e.g. ReactionType via _reactions) rather than a plain .from_dict.
FIELD_PARSE_OVERRIDES: dict[tuple[str, str], str] = {
    ("ReactionCount", "type"): '_reaction_type({d}.get("{k}", {{}}))',
    ("MessageReactionUpdated", "old_reaction"): '_reactions({d}.get("{k}"))',
    ("MessageReactionUpdated", "new_reaction"): '_reactions({d}.get("{k}"))',
}

# Names imported into the generated module from .types (helpers/behavior types
# its parse code references at runtime). The generator already imports the
# behavior/handwritten types a field references; list here only the extras a
# parse/type override needs (e.g. the ReactionType helpers).
EXTRA_IMPORTS_FROM_TYPES: set[str] = {
    "ReactionType",
    "_reaction_type",
    "_reactions",
}
