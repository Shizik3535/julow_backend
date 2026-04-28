from __future__ import annotations

from typing import Any

from app.shared.application.base_event_handler import BaseEventHandler
from app.shared.domain.value_objects.id_vo import Id
from app.context.notification.domain.repositories.notification_preferences_repository import (
    NotificationPreferencesRepository,
)
from app.context.notification.domain.repositories.device_token_repository import DeviceTokenRepository


class OnUserDeletedCleanup(BaseEventHandler[dict[str, Any]]):
    """
    Обработчик события UserDeleted из Identity BC.

    Деактивирует настройки уведомлений и токены устройств пользователя.
    Идемпотентно — пропускает, если данные уже удалены.
    """

    def __init__(
        self,
        preferences_repo: NotificationPreferencesRepository,
        device_token_repo: DeviceTokenRepository,
    ) -> None:
        super().__init__()
        self._preferences_repo = preferences_repo
        self._device_token_repo = device_token_repo

    async def handle(self, event: dict[str, Any]) -> None:
        event_type = event.get("event_type")
        if event_type != "UserDeleted":
            return

        payload = event.get("payload", {})
        user_id_str = payload.get("user_id")
        if not user_id_str:
            return

        user_id = Id.from_string(user_id_str)

        # Удаляем настройки
        preferences = await self._preferences_repo.get_by_user_id(user_id)
        if preferences is not None:
            await self._preferences_repo.delete(preferences.id)

        # Деактивируем все токены устройств
        tokens = await self._device_token_repo.get_by_user_id(user_id)
        for token in tokens:
            token.deactivate()
            await self._device_token_repo.update(token)
