from __future__ import annotations

from app.shared.application.base_dto import BaseDTO
from app.context.notification.application.dto.preference_entry_dto import PreferenceEntryDTO
from app.context.notification.application.dto.project_override_dto import ProjectOverrideDTO


class NotificationPreferencesDTO(BaseDTO):
    """
    DTO настроек уведомлений.

    Атрибуты:
        global_preferences: Глобальные настройки.
        project_overrides: Переопределения на уровне проектов.
        reminder_window_hours: Окно напоминания о дедлайне (в часах).
    """

    global_preferences: list[PreferenceEntryDTO] = []
    project_overrides: list[ProjectOverrideDTO] = []
    reminder_window_hours: int = 24
