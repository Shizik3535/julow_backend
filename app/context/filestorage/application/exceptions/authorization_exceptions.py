from __future__ import annotations

from app.shared.application.application_exceptions import ApplicationException


class InsufficientFileStoragePermissionsException(ApplicationException):
    """Недостаточно разрешений для операции FileStorage."""

    def __init__(self, permission: str = "", workspace_id: str | None = None) -> None:
        msg = "Недостаточно разрешений для операции FileStorage"
        if permission:
            msg += f": требуется «{permission}»"
        if workspace_id:
            msg += f" в workspace {workspace_id}"
        super().__init__(msg)
        self.permission = permission
        self.workspace_id = workspace_id
