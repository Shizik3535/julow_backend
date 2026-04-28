from __future__ import annotations

from abc import abstractmethod

from app.shared.domain.base_repository import RepositoryPort
from app.shared.domain.value_objects.id_vo import Id
from app.context.notification.domain.aggregates.device_token import DeviceToken


class DeviceTokenRepository(RepositoryPort[DeviceToken]):
    """Порт репозитория для агрегата DeviceToken."""

    @abstractmethod
    async def get_by_user_id(self, user_id: Id) -> list[DeviceToken]:
        """Найти все токены устройств пользователя."""

    @abstractmethod
    async def get_active_by_user_id(self, user_id: Id) -> list[DeviceToken]:
        """Найти активные токены устройств пользователя."""

    @abstractmethod
    async def get_by_token(self, token: str) -> DeviceToken | None:
        """Найти токен устройства по значению токена."""
