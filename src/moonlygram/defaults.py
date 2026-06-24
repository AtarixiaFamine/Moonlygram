"""Default values applied to outgoing Bot API calls."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class Defaults:
    """Default parameter values filled in when a Bot method leaves them unset.

    A default applies only to methods that expose the matching parameter (it is
    filled in when the method passes that parameter as None).
    """

    parse_mode: Optional[str] = None
    disable_notification: Optional[bool] = None
    protect_content: Optional[bool] = None
