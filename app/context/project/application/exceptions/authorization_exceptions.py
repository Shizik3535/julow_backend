from __future__ import annotations

from app.shared.application.application_exceptions import ApplicationException


class InsufficientProjectPermissionsException(ApplicationException):
    """У пользователя нет необходимого разрешения в проекте."""

    http_status_code = 403
    error_code = "INSUFFICIENT_PROJECT_PERMISSIONS"

    def __init__(self, permission: str, project_id: str) -> None:
        self.permission = permission
        self.project_id = project_id
        super().__init__(
            f"Недостаточно прав в проекте {project_id}: требуется разрешение «{permission}»"
        )
