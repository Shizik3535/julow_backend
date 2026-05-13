from __future__ import annotations

from app.shared.application.application_exceptions import ApplicationException


class TimeEntryWorkspaceNotFoundException(ApplicationException):
    """Workspace не найден при операции с записью времени."""

    http_status_code = 404
    error_code = "WORKSPACE_NOT_FOUND"

    def __init__(self, workspace_id: str) -> None:
        super().__init__(f"Workspace {workspace_id} не найден")
        self.workspace_id = workspace_id


class TimeEntryTaskNotFoundException(ApplicationException):
    """Задача не найдена при операции с записью времени."""

    http_status_code = 404
    error_code = "TASK_NOT_FOUND"

    def __init__(self, task_id: str) -> None:
        super().__init__(f"Задача {task_id} не найдена")
        self.task_id = task_id


class TimeEntryProjectNotFoundException(ApplicationException):
    """Проект не найден при операции с записью времени."""

    http_status_code = 404
    error_code = "PROJECT_NOT_FOUND"

    def __init__(self, project_id: str) -> None:
        super().__init__(f"Проект {project_id} не найден")
        self.project_id = project_id


class TimeEntryEpicNotFoundException(ApplicationException):
    """Эпик не найден при операции с записью времени."""

    http_status_code = 404
    error_code = "EPIC_NOT_FOUND"

    def __init__(self, epic_id: str) -> None:
        super().__init__(f"Эпик {epic_id} не найден")
        self.epic_id = epic_id


class TimeEntryNotOwnerException(ApplicationException):
    """Только владелец записи может выполнить операцию."""

    http_status_code = 403
    error_code = "TIME_ENTRY_NOT_OWNER"

    def __init__(self, entry_id: str) -> None:
        super().__init__(
            f"Только владелец записи времени {entry_id} может выполнить операцию"
        )
        self.entry_id = entry_id


class TimeEntryHourlyRateRequiredException(ApplicationException):
    """Для billable-записи требуется hourly_rate."""

    http_status_code = 422
    error_code = "HOURLY_RATE_REQUIRED"

    def __init__(self) -> None:
        super().__init__("Для billable-записи требуется hourly_rate")
