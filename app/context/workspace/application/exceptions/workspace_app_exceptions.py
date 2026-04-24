from __future__ import annotations

from app.shared.application.application_exceptions import ApplicationException


class WorkspaceAlreadyExistsException(ApplicationException):
    """Workspace с таким идентификатором уже существует."""

    def __init__(self, identifier: str) -> None:
        super().__init__(f"Workspace с {identifier} уже существует")
        self.identifier = identifier


class OperationNotAllowedForArchivedWorkspaceException(ApplicationException):
    """Операция невозможна для архивированного workspace."""

    def __init__(self, workspace_id: str = "") -> None:
        msg = "Операция невозможна: workspace архивирован"
        if workspace_id:
            msg += f" ({workspace_id})"
        super().__init__(msg)


class OperationNotAllowedForSuspendedWorkspaceException(ApplicationException):
    """Операция невозможна для приостановленного workspace."""

    def __init__(self, workspace_id: str = "") -> None:
        msg = "Операция невозможна: workspace приостановлен"
        if workspace_id:
            msg += f" ({workspace_id})"
        super().__init__(msg)
