from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class IdentityUserPort(ABC):
    """
    Inboard-порт: получение данных пользователя из Identity BC.

    Profile BC использует этот порт для синхронного
    получения данных пользователя (email, status, roles)
    через DI-инъекцию.

    Реализация — адаптер в infrastructure-слое Profile BC,
    который делегирует в IdentityUserProvider (из Identity BC).
    """

    @abstractmethod
    async def get_user(self, user_id: str) -> dict[str, Any] | None:
        """
        Получить данные пользователя по ID.

        Аргументы:
            user_id: Идентификатор пользователя (UUID строка).

        Возвращает:
            Словарь с данными пользователя или None, если не найден.
            Ключи: id, email, status, role_ids, is_email_confirmed.
        """

    @abstractmethod
    async def user_exists(self, user_id: str) -> bool:
        """
        Проверить, существует ли пользователь.

        Аргументы:
            user_id: Идентификатор пользователя.

        Возвращает:
            True, если пользователь существует.
        """
