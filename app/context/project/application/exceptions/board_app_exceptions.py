from __future__ import annotations

from app.shared.application.application_exceptions import ApplicationException


class BoardNotFoundException(ApplicationException):
    """Доска проекта не найдена."""

    def __init__(self, project_id: str = "") -> None:
        msg = "Доска проекта не найдена"
        if project_id:
            msg += f" (project_id={project_id})"
        super().__init__(msg)


class WorkflowStatusHasTasksException(ApplicationException):
    """Нельзя удалить статус workflow — есть задачи в этом статусе."""

    def __init__(self, status_id: str = "") -> None:
        msg = "Нельзя удалить статус workflow: есть задачи в этом статусе"
        if status_id:
            msg += f" ({status_id})"
        super().__init__(msg)
