from __future__ import annotations

from enum import Enum


class ProjectVisibility(Enum):
    """
    Видимость проекта.

    Значения:
        PRIVATE: Только участники видят проект
        WORKSPACE: Все члены workspace видят
        ORGANIZATION: Все члены организации видят
        PUBLIC: Видно всем
    """

    PRIVATE = "private"
    WORKSPACE = "workspace"
    ORGANIZATION = "organization"
    PUBLIC = "public"
