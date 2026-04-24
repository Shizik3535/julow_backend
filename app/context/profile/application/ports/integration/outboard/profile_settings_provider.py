from __future__ import annotations

from abc import ABC, abstractmethod

from app.context.profile.application.dto.profile_settings_dto import ProfileSettingsDTO


class ProfileSettingsProvider(ABC):
    """
    Outboard-порт: предоставляет настройки профиля другим BC.

    Другие BC инжектируют этот порт через DI для синхронного
    получения настроек локализации, приватности и уведомлений.

    Реализация находится в infrastructure-слое Profile BC.
    """

    @abstractmethod
    async def get_settings(self, user_id: str) -> ProfileSettingsDTO | None:
        """
        Получить настройки профиля по user_id.

        Аргументы:
            user_id: Идентификатор пользователя.

        Возвращает:
            ProfileSettingsDTO или None, если профиль не найден.
        """
