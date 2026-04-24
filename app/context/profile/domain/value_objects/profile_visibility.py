from __future__ import annotations

from enum import Enum


class ProfileVisibility(Enum):
    """
    Видимость профиля пользователя.

    Значения:
        PUBLIC: Доступен всем.
        ORGANIZATION_ONLY: Доступен только внутри организации.
        PRIVATE: Приватный.
    """

    PUBLIC = "public"
    ORGANIZATION_ONLY = "organization_only"
    PRIVATE = "private"
