from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class IdentityUserPort(ABC):
    """
    Inboard-порт: получение данных пользователя из Identity BC.

    FileStorage BC использует этот порт для проверки существования
    пользователей при выдаче разрешений на файлы и при передаче владения.
    """

    @abstractmethod
    async def user_exists(self, user_id: str) -> bool:
        """Проверить существование пользователя."""

    @abstractmethod
    async def get_user(self, user_id: str) -> dict[str, Any] | None:
        """Получить данные пользователя (dict) или None."""
