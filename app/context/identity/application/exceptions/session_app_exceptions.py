from __future__ import annotations

from app.shared.application.application_exceptions import ApplicationException


class SessionLimitExceededException(ApplicationException):
    """Превышено максимальное количество одновременных сессий."""

    http_status_code = 409
    error_code = "SESSION_LIMIT_EXCEEDED"

    def __init__(self, max_sessions: int) -> None:
        super().__init__(f"Превышен лимит одновременных сессий: {max_sessions}")
        self.max_sessions = max_sessions


class InvalidRefreshTokenException(ApplicationException):
    """Невалидный или просроченный refresh токен."""

    http_status_code = 401
    error_code = "INVALID_REFRESH_TOKEN"

    def __init__(self) -> None:
        super().__init__("Невалидный или просроченный refresh токен")
