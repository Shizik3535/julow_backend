from __future__ import annotations

from abc import ABC, abstractmethod

from app.context.identity.application.dto.user_dto import UserDTO


class IdentityUserProvider(ABC):
    """
    Outboard-порт: предоставляет данные пользователей другим BC.

    Другие BC инжектируют этот порт через DI для синхронного
    получения данных о пользователях из Identity BC.

    Реализация находится в infrastructure-слое Identity BC.
    """

    @abstractmethod
    async def get_user(self, user_id: str) -> UserDTO | None:
        """
        Получить пользователя по ID.

        Аргументы:
            user_id: Идентификатор пользователя.

        Возвращает:
            UserDTO или None, если не найден.
        """

    @abstractmethod
    async def get_users(self, user_ids: list[str]) -> list[UserDTO]:
        """
        Получить список пользователей по ID.

        Аргументы:
            user_ids: Список идентификаторов пользователей.

        Возвращает:
            Список UserDTO.
        """

    @abstractmethod
    async def get_user_by_email(self, email: str) -> UserDTO | None:
        """
        Найти пользователя по email.

        Используется для маршрутизации уведомлений на email-приглашения:
        когда приглашение шлётся на адрес уже зарегистрированного user'а,
        мы хотим положить ему in-app notification с кнопками «принять/
        отклонить», а не только email-ссылку.

        Аргументы:
            email: Email-адрес (без нормализации; реализация может
                выполнить trim/lowercase согласно Email VO).

        Возвращает:
            UserDTO или None, если пользователь не найден.
        """
