from __future__ import annotations

from app.shared.domain.exceptions import BusinessRuleViolationException, EntityNotFoundException


class SprintNotFoundException(EntityNotFoundException):
    """Спринт не найден."""

    def __init__(self, id: object) -> None:
        super().__init__(entity_type="Sprint", id=id)


class SprintAlreadyStartedException(BusinessRuleViolationException):
    """Спринт уже запущен."""

    def __init__(self) -> None:
        super().__init__(
            rule="SprintAlreadyStarted",
            message="Спринт уже запущен",
        )


class SprintNotStartedException(BusinessRuleViolationException):
    """Спринт не запущен."""

    def __init__(self) -> None:
        super().__init__(
            rule="SprintNotStarted",
            message="Спринт не запущен",
        )


class CannotCompleteSprintWithOpenTasksException(BusinessRuleViolationException):
    """Нельзя завершить спринт с открытыми задачами."""

    def __init__(self) -> None:
        super().__init__(
            rule="NoCompleteSprintWithOpenTasks",
            message="Нельзя завершить спринт с открытыми задачами",
        )
