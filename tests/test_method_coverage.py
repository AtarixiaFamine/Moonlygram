"""Guards that keep Bot's method signatures honest against the vendored spec.

Bot's methods are hand-written, so nothing stops a spec parameter from being
quietly left out; that is how forum topics, disable_notification, and much of
the media surface once went missing while the generated types stayed current.
These tests read codegen/api.json and fail when a modelled method omits a
parameter the spec defines, or when a spec method is neither modelled nor
recorded as an explicit decision.

The check is one-directional: every spec parameter must appear in the
signature, but a signature may carry extras. The library models Bot API 10.2
while the vendored spec is 10.1, and a few parameters are deliberately exposed
under friendlier names (see DIVERGENCES).
"""
from __future__ import annotations

import inspect
import json
import re
from pathlib import Path

import pytest

from moonlygram import Bot

ROOT = Path(__file__).resolve().parent.parent
SPEC = json.loads((ROOT / "codegen" / "api.json").read_text(encoding="utf-8"))

# Spec parameters a method deliberately does not expose verbatim, and why. Each
# entry is a standing decision, not a gap: adding one here means the capability
# is reachable, just spelled differently.
DIVERGENCES: dict[str, dict[str, str]] = {
    "send_rich_message": {
        "rich_message": "split into html / markdown / blocks / media",
    },
    "send_rich_message_draft": {
        "rich_message": "split into html / markdown / blocks / media",
    },
    "edit_message_text": {
        "rich_message": "exposed as the separate edit_rich_message_text method",
    },
}

# Bot attributes whose name matches a spec method but means something else.
# Bot.close() closes the local HTTP session; the API's close closes the bot
# instance on Telegram's side. Neither delegates to the other.
NAME_COLLISIONS = {"close"}

# Spec methods with no Bot wrapper, grouped by domain. Every unmodelled method
# must appear here, so leaving one out is a recorded decision rather than an
# oversight: refreshing the spec to a new API version fails the completeness
# test until each new method is either implemented or added to this list. The
# escape hatch bot.call() reaches all of them in the meantime.
UNIMPLEMENTED = {
    # lifecycle (getUpdates is driven by ext.Application, not exposed on Bot)
    "getUpdates",
    "logOut",
    "close",  # see NAME_COLLISIONS
    # games
    "sendGame",
    "setGameScore",
    "getGameHighScores",
    # stories
    "postStory",
    "editStory",
    "deleteStory",
    "repostStory",
    "sendLivePhoto",
    # business accounts and connections
    "getBusinessConnection",
    "readBusinessMessage",
    "deleteBusinessMessages",
    "setBusinessAccountName",
    "setBusinessAccountUsername",
    "setBusinessAccountBio",
    "setBusinessAccountProfilePhoto",
    "removeBusinessAccountProfilePhoto",
    "setBusinessAccountGiftSettings",
    "getBusinessAccountStarBalance",
    "getBusinessAccountGifts",
    "transferBusinessAccountStars",
    # gifts and premium
    "sendGift",
    "getAvailableGifts",
    "getChatGifts",
    "getUserGifts",
    "transferGift",
    "upgradeGift",
    "convertGiftToStars",
    "giftPremiumSubscription",
    # checklists and paid media
    "sendChecklist",
    "editMessageChecklist",
    "sendPaidMedia",
    # verification
    "verifyChat",
    "verifyUser",
    "removeChatVerification",
    "removeUserVerification",
    # suggested posts (the parameters are modelled; the moderation calls not yet)
    "approveSuggestedPost",
    "declineSuggestedPost",
    # subscription invite links
    "createChatSubscriptionInviteLink",
    "editChatSubscriptionInviteLink",
    # reactions beyond setMessageReaction
    "deleteMessageReaction",
    "deleteAllMessageReactions",
    # profile, presence, and account surface
    "setMyProfilePhoto",
    "removeMyProfilePhoto",
    "setUserEmojiStatus",
    "getUserProfileAudios",
    "getUserPersonalChatMessages",
    "setChatMemberTag",
    # prepared inline content and web apps
    "savePreparedInlineMessage",
    "savePreparedKeyboardButton",
    "sendChatJoinRequestWebApp",
    "answerChatJoinRequestQuery",
    "answerGuestQuery",
    # drafts
    "sendMessageDraft",
    # managed bots
    "getManagedBotAccessSettings",
    "setManagedBotAccessSettings",
    "getManagedBotToken",
    "replaceManagedBotToken",
    # passport
    "setPassportDataErrors",
}


def _snake(name: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


def _modelled() -> dict[str, str]:
    """Map spec method name to Bot attribute name, for methods Bot models."""
    found = {}
    for spec_name in SPEC["methods"]:
        attr = _snake(spec_name)
        if attr in NAME_COLLISIONS:
            continue
        if callable(getattr(Bot, attr, None)):
            found[spec_name] = attr
    return found


MODELLED = _modelled()


@pytest.mark.parametrize("spec_name", sorted(MODELLED))
def test_method_exposes_every_spec_parameter(spec_name: str) -> None:
    attr = MODELLED[spec_name]
    params = set(inspect.signature(getattr(Bot, attr)).parameters)
    allowed = DIVERGENCES.get(attr, {})

    spec_params = {f["name"] for f in SPEC["methods"][spec_name].get("fields", [])}
    missing = sorted(spec_params - params - set(allowed))

    assert not missing, (
        f"Bot.{attr} does not accept {', '.join(missing)}, which "
        f"{spec_name} defines. Add the parameter, or record a deliberate "
        f"divergence in DIVERGENCES."
    )


def test_divergences_are_real() -> None:
    """A divergence must name a method and a parameter that actually exist."""
    for attr, entries in DIVERGENCES.items():
        assert callable(getattr(Bot, attr, None)), f"Bot.{attr} no longer exists"
        spec_name = next(s for s, a in MODELLED.items() if a == attr)
        spec_params = {f["name"] for f in SPEC["methods"][spec_name].get("fields", [])}
        stale = sorted(set(entries) - spec_params)
        assert not stale, (
            f"DIVERGENCES[{attr!r}] lists {', '.join(stale)}, which "
            f"{spec_name} no longer defines; drop the entry."
        )


def test_unimplemented_list_is_accurate() -> None:
    """Nothing in UNIMPLEMENTED should have quietly grown a Bot method."""
    now_implemented = sorted(name for name in UNIMPLEMENTED if name in MODELLED)
    assert not now_implemented, (
        f"{', '.join(now_implemented)} is implemented now; "
        f"remove it from UNIMPLEMENTED."
    )


def test_every_spec_method_is_modelled_or_recorded() -> None:
    """A spec method must be a Bot method or a recorded UNIMPLEMENTED entry.

    This is what makes a spec refresh loud: a new API version's methods fail
    here until each is implemented or consciously deferred.
    """
    unaccounted = sorted(set(SPEC["methods"]) - set(MODELLED) - UNIMPLEMENTED)
    assert not unaccounted, (
        f"{', '.join(unaccounted)} is in the spec but neither modelled nor "
        f"listed in UNIMPLEMENTED; implement it or record the deferral."
    )
    unknown = sorted(UNIMPLEMENTED - set(SPEC["methods"]))
    assert not unknown, (
        f"UNIMPLEMENTED lists {', '.join(unknown)}, which the spec does not "
        f"define; drop the entry."
    )
