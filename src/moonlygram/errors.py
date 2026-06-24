"""Exception hierarchy for Moonlygram.

Every exception raised by the library derives from MoonlygramError, so
``except MoonlygramError`` catches all of them. The two branches below it are
APIError (Telegram replied with ok: false, so there is an error_code) and
NetworkError (the request never produced a reply — a transport failure).

Telegram's HTTP status codes map to named APIError subclasses so callers can
branch on the kind of failure without inspecting error_code by hand::

    try:
        await bot.send_message(chat_id, text)
    except Forbidden:
        ...  # the bot was blocked or kicked
    except BadRequest:
        ...  # malformed request
"""
from __future__ import annotations

from typing import Any, Optional


class MoonlygramError(Exception):
    """Base class for every error Moonlygram raises."""


class InvalidToken(MoonlygramError):
    """The bot token is missing or malformed before any request was made."""


class NetworkError(MoonlygramError):
    """The request failed at the transport layer, with no reply from Telegram.

    Wraps the underlying httpx error (connection refused, DNS failure, a
    dropped connection); the original is available as ``__cause__``.
    """


class TimedOut(NetworkError):
    """The request did not complete before the timeout elapsed."""


class APIError(MoonlygramError):
    """Telegram replied with ``ok: false``.

    Exposes the response fields so callers can branch on error_code. Named
    subclasses cover the common HTTP status codes.
    """

    def __init__(self, error_code: int, description: str, method: str) -> None:
        self.error_code = error_code
        self.description = description
        self.method = method
        super().__init__(f"[{error_code}] {description} (while calling {method!r})")


class BadRequest(APIError):
    """400 — the request was malformed or referred to something that is gone."""

    def __init__(self, description: str, method: str) -> None:
        super().__init__(400, description, method)


class Unauthorized(APIError):
    """401 — the bot token is missing, malformed, or revoked."""

    def __init__(self, description: str, method: str) -> None:
        super().__init__(401, description, method)


class Forbidden(APIError):
    """403 — the bot lacks rights for the action (blocked, kicked, no admin)."""

    def __init__(self, description: str, method: str) -> None:
        super().__init__(403, description, method)


class NotFound(APIError):
    """404 — the method or resource does not exist."""

    def __init__(self, description: str, method: str) -> None:
        super().__init__(404, description, method)


class Conflict(APIError):
    """409 — conflicting state, e.g. polling while a webhook is set."""

    def __init__(self, description: str, method: str) -> None:
        super().__init__(409, description, method)


class FloodWait(APIError):
    """429 — you're being rate-limited and must wait ``retry_after`` seconds."""

    def __init__(self, retry_after: int, description: str, method: str) -> None:
        self.retry_after = retry_after
        super().__init__(429, description, method)


class ChatMigrated(APIError):
    """The group migrated to a supergroup with id ``migrate_to_chat_id``.

    Telegram returns this as a 400; resend to the new id.
    """

    def __init__(
        self, migrate_to_chat_id: int, description: str, method: str
    ) -> None:
        self.migrate_to_chat_id = migrate_to_chat_id
        super().__init__(400, description, method)


def error_from_response(
    error_code: int,
    description: str,
    method: str,
    parameters: Optional[dict[str, Any]] = None,
) -> APIError:
    """Build the most specific APIError for an ok: false response.

    Used by the Session to turn ``{error_code, description, parameters}`` into a
    named exception. retry_after and migrate_to_chat_id, when present in
    parameters, win over the plain status-code mapping.
    """
    parameters = parameters or {}
    if "migrate_to_chat_id" in parameters:
        return ChatMigrated(parameters["migrate_to_chat_id"], description, method)
    if error_code == 429 or "retry_after" in parameters:
        return FloodWait(parameters.get("retry_after", 1), description, method)
    by_code = {
        400: BadRequest,
        401: Unauthorized,
        403: Forbidden,
        404: NotFound,
        409: Conflict,
    }
    cls = by_code.get(error_code)
    if cls is not None:
        return cls(description, method)
    return APIError(error_code, description, method)
