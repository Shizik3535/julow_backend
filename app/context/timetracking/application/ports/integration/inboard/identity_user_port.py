from __future__ import annotations

from abc import ABC, abstractmethod


class IdentityUserPort(ABC):
    """
    Inboard-порт: получение данных пользователя из Identity BC.

    TimeTracking BC использует для проверки существования пользователей
    при утверждении/отклонении записей.
    """

    @abstractmethod
    async def user_exists(self, user_id: str) -> bool:
        """Проверить существование пользователя."""
