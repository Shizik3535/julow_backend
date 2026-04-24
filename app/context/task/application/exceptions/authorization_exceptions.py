from __future__ import annotations

from app.shared.application.application_exceptions import ApplicationException


class InsufficientTaskPermissionsException(ApplicationException):
    """У пользователя нет необходимого разрешения для операции с задачей."""

    http_status_code = 403
    error_code = "INSUFFICIENT_TASK_PERMISSIONS"

    def __init__(self, permission: str, project_id: str, user_id: str | None = None) -> None:
        self.permission = permission
        self.project_id = project_id
        self.user_id = user_id
        super().__init__(
            f"Недостаточно прав в задачах проекта {project_id}: "
            f"требуется разрешение «{permission}»"
        )
