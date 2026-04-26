from __future__ import annotations

from app.shared.application.application_exceptions import ApplicationException


class OrganizationNotFoundException(ApplicationException):
    """Организация не найдена."""

    http_status_code = 404
    error_code = "ORGANIZATION_NOT_FOUND"

    def __init__(self, org_id: str) -> None:
        super().__init__(f"Организация {org_id} не найдена")
        self.org_id = org_id
