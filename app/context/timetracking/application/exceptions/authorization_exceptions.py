from __future__ import annotations

from app.shared.application.application_exceptions import ApplicationException


class InsufficientTimeTrackingPermissionsException(ApplicationException):
    """У пользователя нет необходимого разрешения для операции с записями времени."""

    http_status_code = 403
    error_code = "INSUFFICIENT_TIMETRACKING_PERMISSIONS"

    def __init__(self, permission: str, workspace_id: str, user_id: str | None = None) -> None:
        self.permission = permission
        self.workspace_id = workspace_id
        self.user_id = user_id
        super().__init__(
            f"Недостаточно прав в workspace {workspace_id}: "
            f"требуется разрешение «{permission}»"
        )
