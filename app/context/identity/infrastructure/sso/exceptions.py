from __future__ import annotations

from app.shared.application.application_exceptions import ApplicationException


class SSOAuthenticationException(ApplicationException):
    """Ошибка аутентификации через SSO."""

    http_status_code = 401
    error_code = "SSO_AUTHENTICATION_FAILED"

    def __init__(self, message: str = "SSO-аутентификация не удалась") -> None:
        super().__init__(message)
