from __future__ import annotations

from app.shared.application.application_exceptions import ApplicationException


class InvalidTokenException(ApplicationException):
    """JWT токен невалиден или истёк."""

    http_status_code = 401
    error_code = "INVALID_TOKEN"

    def __init__(self, detail: str = "Invalid or expired token") -> None:
        super().__init__(detail)
