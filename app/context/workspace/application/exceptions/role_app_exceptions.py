from __future__ import annotations

from app.shared.application.application_exceptions import ApplicationException


class DuplicateRoleNameException(ApplicationException):
    """Роль с таким названием уже существует в workspace."""

    http_status_code = 409
    error_code = "DUPLICATE_ROLE_NAME"

    def __init__(self, name: str, workspace_id: str) -> None:
        super().__init__(
            f"Роль «{name}» уже существует в workspace {workspace_id}"
        )
        self.name = name
        self.workspace_id = workspace_id
