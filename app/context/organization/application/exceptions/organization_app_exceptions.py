from __future__ import annotations

from app.shared.application.application_exceptions import ApplicationException


class OrganizationAlreadyExistsException(ApplicationException):
    """Организация с таким именем уже существует."""

    def __init__(self, name: str) -> None:
        super().__init__(f"Организация с именем «{name}» уже существует")
        self.name = name


class OperationNotAllowedForSuspendedOrgException(ApplicationException):
    """Операция невозможна для приостановленной организации."""

    def __init__(self, org_id: str) -> None:
        super().__init__(f"Операция невозможна: организация {org_id} приостановлена")
        self.org_id = org_id
