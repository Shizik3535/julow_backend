from __future__ import annotations

from typing import Any

from app.shared.application.base_event_handler import BaseEventHandler
from app.shared.domain.value_objects.id_vo import Id
from app.context.notification.domain.aggregates.notification_preferences import NotificationPreferences
from app.context.notification.domain.repositories.notification_preferences_repository import (
    NotificationPreferencesRepository,
)
from app.core.logging import get_logger

logger = get_logger(__name__)


class OnUserRegisteredCreatePreferences(BaseEventHandler[dict[str, Any]]):
    """
    Обработчик события UserRegistered из Identity BC.

    Создаёт NotificationPreferences для нового пользователя.
    Идемпотентно — пропускает, если настройки уже существуют.
    """

    def __init__(self, preferences_repo: NotificationPreferencesRepository) -> None:
        super().__init__()
        self._repo = preferences_repo

    async def handle(self, event: dict[str, Any]) -> None:
        event_type = event.get("event_type")
        if event_type != "UserRegistered":
            return

        payload = event.get("payload", {})
        user_id_str = payload.get("user_id")
        if not user_id_str:
            self._logger.warning("Event missing user_id", event=event)
            return

        user_id = Id.from_string(user_id_str)

        # Идемпотентность
        existing = await self._repo.get_by_user_id(user_id)
        if existing is not None:
            self._logger.warning("Preferences already exist, skipping", user_id=user_id_str)
            return

        preferences = NotificationPreferences.create(user_id=user_id)

        try:
            await self._repo.add(preferences)
        except Exception as exc:
            # Race condition: конкурентный запрос уже вставил запись (unique constraint on user_id)
            if "unique" in str(exc).lower() or "duplicate" in str(exc).lower() or "UniqueViolation" in type(exc).__name__:
                self._logger.warning("Preferences concurrently created, skipping", user_id=user_id_str)
                return
            raise
