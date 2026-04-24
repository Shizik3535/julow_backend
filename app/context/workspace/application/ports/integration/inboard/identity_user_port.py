from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class IdentityUserPort(ABC):
    """
    Inboard-порт: получение данных пользователя из Identity BC.

    Workspace BC использует этот порт для проверки существования
    пользователей при добавлении участников и принятии приглашений.
    Реализация — адаптер в infrastructure, делегирующий в
    IdentityUserProvider (outboard Identity BC).
    """

    @abstractmethod
    async def user_exists(self, user_id: str) -> bool:
        """Проверить существование пользователя."""

    @abstractmethod
    async def get_user(self, user_id: str) -> dict[str, Any] | None:
        """Получить данные пользователя (dict) или None."""
