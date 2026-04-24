from __future__ import annotations

from app.shared.application.application_exceptions import ApplicationException


class ProjectAlreadyExistsException(ApplicationException):
    """Проект с таким идентификатором уже существует."""

    def __init__(self, identifier: str) -> None:
        super().__init__(f"Проект с {identifier} уже существует")
        self.identifier = identifier


class OperationNotAllowedForArchivedProjectException(ApplicationException):
    """Операция невозможна для архивированного проекта."""

    def __init__(self, project_id: str = "") -> None:
        msg = "Операция невозможна: проект архивирован"
        if project_id:
            msg += f" ({project_id})"
        super().__init__(msg)


class OperationNotAllowedForSuspendedProjectException(ApplicationException):
    """Операция невозможна для приостановленного проекта."""

    def __init__(self, project_id: str = "") -> None:
        msg = "Операция невозможна: проект приостановлен"
        if project_id:
            msg += f" ({project_id})"
        super().__init__(msg)
