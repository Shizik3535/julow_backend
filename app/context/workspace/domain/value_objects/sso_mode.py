from __future__ import annotations

from enum import Enum


class SSOMode(Enum):
    """
    Режим SSO для workspace.

    Значения:
        NONE: SSO не используется
        OPTIONAL: SSO опционально
        REQUIRED: SSO обязательно
    """

    NONE = "none"
    OPTIONAL = "optional"
    REQUIRED = "required"
