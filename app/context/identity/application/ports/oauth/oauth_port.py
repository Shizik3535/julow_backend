from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class OAuthUserInfo:
    """
    Информация о пользователе от OAuth-провайдера.

    Атрибуты:
        provider_user_id: ID пользователя у провайдера.
        email: Email от провайдера (может быть None).
        display_name: Отображаемое имя (может быть None).
    """

    provider_user_id: str
    email: str | None = None
    display_name: str | None = None


class OAuthPort(ABC):
    """
    BC-специфичный порт для работы с OAuth-провайдерами.

    Абстрагирует обмен authorization code на access token
    и получение профиля пользователя от провайдера.

    Реализация (адаптер) находится в infrastructure-слое Identity BC.
    """

    @abstractmethod
    async def exchange_code(
        self, provider: str, code: str, redirect_uri: str
    ) -> str:
        """
        Обменять authorization code на access token.

        Аргументы:
            provider: Название провайдера (oauth_google, oauth_github, ...).
            code: Authorization code от провайдера.
            redirect_uri: URI перенаправления (должен совпадать с тем, что был при авторизации).

        Возвращает:
            Access token от провайдера.

        Выбрасывает:
            OAuthException: Ошибка обмена кода.
        """

    @abstractmethod
    async def get_user_info(self, provider: str, access_token: str) -> OAuthUserInfo:
        """
        Получить информацию о пользователе от провайдера.

        Аргументы:
            provider: Название провайдера.
            access_token: Access token от провайдера.

        Возвращает:
            OAuthUserInfo с данными пользователя.

        Выбрасывает:
            OAuthException: Ошибка получения данных.
        """
