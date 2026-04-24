from __future__ import annotations

from app.shared.application.application_exceptions import ApplicationException


class UserAlreadyExistsException(ApplicationException):
    """Пользователь с таким email уже зарегистрирован."""

    http_status_code = 409
    error_code = "USER_ALREADY_EXISTS"

    def __init__(self, email: str) -> None:
        super().__init__(f"Пользователь с email {email} уже существует")
        self.email = email
