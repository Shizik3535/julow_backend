from __future__ import annotations

from app.shared.application.application_exceptions import ApplicationException


class InsufficientPermissionsException(ApplicationException):
    """У пользователя нет необходимого разрешения."""

    http_status_code = 403
    error_code = "INSUFFICIENT_PERMISSIONS"

    def __init__(self, permission: str) -> None:
        self.permission = permission
        super().__init__(f"Недостаточно прав: требуется разрешение «{permission}»")
