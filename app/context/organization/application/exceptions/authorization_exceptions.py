from __future__ import annotations

from app.shared.application.application_exceptions import ApplicationException


class InsufficientOrgPermissionsException(ApplicationException):
    """У пользователя нет необходимого разрешения в организации."""

    http_status_code = 403
    error_code = "INSUFFICIENT_ORG_PERMISSIONS"

    def __init__(self, permission: str, org_id: str) -> None:
        self.permission = permission
        self.org_id = org_id
        super().__init__(
            f"Недостаточно прав в организации {org_id}: требуется разрешение «{permission}»"
        )
