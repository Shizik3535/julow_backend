from __future__ import annotations

from abc import ABC, abstractmethod


class IdentityUserPort(ABC):
    """
    Inboard-порт: проверка существования пользователя (Identity BC).

    Используется для ACL-проверок при назначении исполнителей,
    наблюдателей и авторов задач.
    """

    @abstractmethod
    async def user_exists(self, user_id: str) -> bool:
        """Проверить существование пользователя."""
