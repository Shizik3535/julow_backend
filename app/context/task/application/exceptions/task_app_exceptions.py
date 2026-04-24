from __future__ import annotations

from app.shared.application.application_exceptions import ApplicationException


class TaskProjectNotFoundException(ApplicationException):
    """Проект не найден при операции с задачей."""

    def __init__(self, project_id: str) -> None:
        super().__init__(f"Проект {project_id} не найден")
        self.project_id = project_id


class TaskProjectArchivedOrSuspendedException(ApplicationException):
    """Проект архивирован или приостановлен — операции с задачами невозможны."""

    def __init__(self, project_id: str) -> None:
        super().__init__(f"Проект {project_id} архивирован или приостановлен")
        self.project_id = project_id


class TaskStatusTransitionNotAllowedException(ApplicationException):
    """Переход между workflow-статусами не разрешён."""

    def __init__(self, from_status_id: str, to_status_id: str) -> None:
        super().__init__(
            f"Переход статуса {from_status_id} → {to_status_id} не разрешён workflow"
        )
        self.from_status_id = from_status_id
        self.to_status_id = to_status_id


class TaskSprintNotAvailableException(ApplicationException):
    """Спринт недоступен для назначения задачи."""

    def __init__(self, sprint_id: str, reason: str = "") -> None:
        msg = f"Спринт {sprint_id} недоступен"
        if reason:
            msg += f": {reason}"
        super().__init__(msg)
        self.sprint_id = sprint_id


class TaskEpicNotAvailableException(ApplicationException):
    """Эпик недоступен для привязки задачи."""

    def __init__(self, epic_id: str, reason: str = "") -> None:
        msg = f"Эпик {epic_id} недоступен"
        if reason:
            msg += f": {reason}"
        super().__init__(msg)
        self.epic_id = epic_id


class TaskHierarchyDepthLimitException(ApplicationException):
    """Превышена максимальная глубина иерархии задач."""

    def __init__(self, max_depth: int) -> None:
        super().__init__(f"Максимальная глубина иерархии: {max_depth}")
        self.max_depth = max_depth


class TaskCustomFieldValidationException(ApplicationException):
    """Ошибка валидации кастомного поля задачи."""

    def __init__(self, field_name: str, reason: str = "") -> None:
        msg = f"Ошибка валидации кастомного поля '{field_name}'"
        if reason:
            msg += f": {reason}"
        super().__init__(msg)
        self.field_name = field_name


class TaskColumnWipLimitExceededException(ApplicationException):
    """WIP-лимит колонки превышен."""

    def __init__(self, column_id: str) -> None:
        super().__init__(f"WIP-лимит колонки {column_id} превышен")
        self.column_id = column_id
