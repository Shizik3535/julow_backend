from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class IdentityUserPort(ABC):
    """Inboard-порт: получение данных пользователя из Identity BC."""

    @abstractmethod
    async def get_user(self, user_id: str) -> dict[str, Any] | None:
        """Получить данные пользователя по ID."""

    @abstractmethod
    async def user_exists(self, user_id: str) -> bool:
        """Проверить существование пользователя."""

    @abstractmethod
    async def get_user_by_email(self, email: str) -> dict[str, Any] | None:
        """
        Найти пользователя по email.

        Используется обработчиком `OnProjectInvitationSentNotify`, чтобы
        понять, есть ли в системе пользователь с таким email — если есть,
        мы кладём ему in-app notification с кнопками accept/decline.
        Если такого пользователя нет, notification не создаётся (приглашение
        всё ещё дойдёт по email-flow через `/invite/<token>`).
        """
