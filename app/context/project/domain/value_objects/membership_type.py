from __future__ import annotations

from enum import Enum


class MembershipType(str, Enum):
    """
    Тип членства в проекте.

    STANDARD — полный участник (член workspace).
    GUEST — гостевой участник (без членства в workspace).
    """

    STANDARD = "STANDARD"
    GUEST = "GUEST"
