from __future__ import annotations

from app.shared.application.application_exceptions import ApplicationException


class InsufficientWorkspacePermissionsException(ApplicationException):
    """У пользователя нет необходимого разрешения в workspace."""

    http_status_code = 403
    error_code = "INSUFFICIENT_WORKSPACE_PERMISSIONS"

    def __init__(self, permission: str, workspace_id: str) -> None:
        self.permission = permission
        self.workspace_id = workspace_id
        super().__init__(
            f"Недостаточно прав в workspace {workspace_id}: требуется разрешение «{permission}»"
        )
