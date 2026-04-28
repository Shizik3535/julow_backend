from __future__ import annotations

from app.shared.application.base_dto import BaseDTO
from app.context.notification.application.dto.preference_entry_dto import PreferenceEntryDTO


class ProjectOverrideDTO(BaseDTO):
    """
    DTO переопределения настроек на уровне проекта.

    Атрибуты:
        project_id: ID проекта.
        preferences: Настройки для проекта.
    """

    project_id: str = ""
    preferences: list[PreferenceEntryDTO] = []
