from __future__ import annotations

from abc import ABC, abstractmethod

from app.context.profile.application.dto.profile_dto import ProfileDTO


class ProfileUserProvider(ABC):
    """
    Outboard-порт: предоставляет публичный профиль другим BC.

    Другие BC инжектируют этот порт через DI для синхронного
    получения данных профиля пользователя из Profile BC.

    Реализация находится в infrastructure-слое Profile BC.
    """

    @abstractmethod
    async def get_profile(self, user_id: str) -> ProfileDTO | None:
        """
        Получить профиль по user_id.

        Аргументы:
            user_id: Идентификатор пользователя (из Identity BC).

        Возвращает:
            ProfileDTO или None, если не найден.
        """

    @abstractmethod
    async def get_profiles(self, user_ids: list[str]) -> list[ProfileDTO]:
        """
        Получить профили по списку user_id.

        Аргументы:
            user_ids: Список идентификаторов пользователей.

        Возвращает:
            Список ProfileDTO.
        """
