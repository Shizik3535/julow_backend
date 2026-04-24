from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class IdentityUserPort(ABC):
    """
    Inboard-порт: получение данных пользователя из Identity BC.

    Organization BC использует этот порт для проверки существования
    пользователя при добавлении участников, принятии приглашений
    и назначении в команды/департаменты.

    Реализация — адаптер в infrastructure-слое Organization BC,
    который делегирует в IdentityUserProvider из Identity BC.
    """

    @abstractmethod
    async def user_exists(self, user_id: str) -> bool:
        """
        Проверить, существует ли пользователь.

        Аргументы:
            user_id: Идентификатор пользователя (UUID строка).

        Возвращает:
            True, если пользователь существует.
        """

    @abstractmethod
    async def get_user(self, user_id: str) -> dict[str, Any] | None:
        """
        Получить данные пользователя.

        Аргументы:
            user_id: Идентификатор пользователя (UUID строка).

        Возвращает:
            Словарь с данными пользователя или None.
        """
