from __future__ import annotations

from abc import ABC, abstractmethod

from app.shared.application.ports.auth.auth_dto import AccessToken, TokenPair, TokenPayload
from app.shared.application.ports.auth.auth_exceptions import InvalidTokenException


class AuthTokenPort(ABC):
    """
    Порт для работы с JWT токенами (Auth Token Port).

    Абстрагирует генерацию и валидацию JWT токенов.
    Infrastructure-слой реализует этот порт (PyJWT, python-jose и т.д.).

    Правила:
        - Генерация и валидация — синхронные (CPU-bound, нет I/O)
        - Access токен — краткоживущий, для авторизации запросов
        - Refresh токен — долгоживущий, для обновления access токена
    """

    @abstractmethod
    def generate_access_token(self, user_id: str) -> AccessToken:
        """
        Сгенерировать только access токен.

        Аргументы:
            user_id: Идентификатор пользователя (UUID строка).

        Возвращает:
            AccessToken с access токеном.
        """

    @abstractmethod
    def generate_token_pair(self, user_id: str) -> TokenPair:
        """
        Сгенерировать пару JWT токенов для пользователя.

        Аргументы:
            user_id: Идентификатор пользователя (UUID строка).

        Возвращает:
            TokenPair с access и refresh токенами.
        """

    @abstractmethod
    def validate_access_token(self, token: str) -> TokenPayload:
        """
        Валидировать access токен.

        Аргументы:
            token: JWT access токен.

        Возвращает:
            TokenPayload с данными токена.

        Выбрасывает:
            InvalidTokenException: Токен невалиден или истёк.
        """

    @abstractmethod
    def validate_refresh_token(self, token: str) -> TokenPayload:
        """
        Валидировать refresh токен.

        Аргументы:
            token: JWT refresh токен.

        Возвращает:
            TokenPayload с данными токена.

        Выбрасывает:
            InvalidTokenException: Токен невалиден или истёк.
        """
