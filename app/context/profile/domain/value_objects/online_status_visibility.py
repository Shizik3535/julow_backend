from __future__ import annotations

from enum import Enum


class OnlineStatusVisibility(Enum):
    """
    Видимость онлайн-статуса.

    Значения:
        EVERYONE: Виден всем.
        CONTACTS_ONLY: Виден только контактам.
        NOBODY: Никому не виден.
    """

    EVERYONE = "everyone"
    CONTACTS_ONLY = "contacts_only"
    NOBODY = "nobody"
