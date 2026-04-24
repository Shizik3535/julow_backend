from __future__ import annotations

from app.shared.domain.exceptions import EntityNotFoundException


class NotificationNotFoundException(EntityNotFoundException):
    """Уведомление не найдено."""

    def __init__(self, id: object) -> None:
        super().__init__(entity_type="Notification", id=id)


class NotificationPreferencesNotFoundException(EntityNotFoundException):
    """Настройки уведомлений не найдены."""

    def __init__(self, id: object) -> None:
        super().__init__(entity_type="NotificationPreferences", id=id)
