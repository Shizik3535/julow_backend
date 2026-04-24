from __future__ import annotations

from app.shared.domain.base_exceptions import DomainException
from app.shared.domain.exceptions import BusinessRuleViolationException, EntityNotFoundException


class TaskNotFoundException(EntityNotFoundException):
    """Задача не найдена."""

    def __init__(self, id: object) -> None:
        super().__init__(entity_type="Task", id=id)


class TaskArchivedException(DomainException):
    """Задача архивирована, действие невозможно."""

    def __init__(self) -> None:
        super().__init__("Задача архивирована, действие невозможно")


class CannotChangeStatusException(DomainException):
    """Переход статуса не разрешён workflow."""

    def __init__(self, reason: str = "") -> None:
        msg = "Переход статуса не разрешён"
        if reason:
            msg += f": {reason}"
        super().__init__(msg)


class CircularDependencyException(BusinessRuleViolationException):
    """Циклическая зависимость между задачами."""

    def __init__(self) -> None:
        super().__init__(
            rule="NoCircularDependency",
            message="Циклическая зависимость между задачами",
        )


class TaskHierarchyDepthExceededException(BusinessRuleViolationException):
    """Превышена максимальная глубина иерархии."""

    def __init__(self, max_depth: int = 0) -> None:
        super().__init__(
            rule="MaxTaskHierarchyDepth",
            message=f"Превышена максимальная глубина иерархии{f' (максимум: {max_depth})' if max_depth else ''}",
        )


class InvalidTaskRelationException(BusinessRuleViolationException):
    """Некорректная связь."""

    def __init__(self, reason: str = "") -> None:
        super().__init__(
            rule="InvalidTaskRelation",
            message=f"Некорректная связь{f': {reason}' if reason else ''}",
        )


class CannotRelateTaskToSelfException(BusinessRuleViolationException):
    """Нельзя связать задачу саму с собой."""

    def __init__(self) -> None:
        super().__init__(
            rule="NoSelfRelation",
            message="Нельзя связать задачу саму с собой",
        )


class DuplicateRelationException(BusinessRuleViolationException):
    """Связь уже существует."""

    def __init__(self) -> None:
        super().__init__(
            rule="UniqueRelation",
            message="Связь уже существует (same related_task_id + relation_type)",
        )


class ChecklistNotFoundException(EntityNotFoundException):
    """Чек-лист не найден."""

    def __init__(self, id: object) -> None:
        super().__init__(entity_type="Checklist", id=id)


class ChecklistItemNotFoundException(EntityNotFoundException):
    """Пункт чек-листа не найден."""

    def __init__(self, id: object) -> None:
        super().__init__(entity_type="ChecklistItem", id=id)


class DuplicateWatcherException(BusinessRuleViolationException):
    """Наблюдатель уже подписан."""

    def __init__(self, user_id: str = "") -> None:
        super().__init__(
            rule="UniqueWatcher",
            message=f"Наблюдатель уже подписан{f': {user_id}' if user_id else ''}",
        )


class DuplicateLabelException(BusinessRuleViolationException):
    """Метка с таким именем уже существует на задаче."""

    def __init__(self, name: str = "") -> None:
        super().__init__(
            rule="UniqueLabel",
            message=f"Метка с таким именем уже существует{f': {name}' if name else ''}",
        )


class EffortUnitMismatchException(BusinessRuleViolationException):
    """Единицы оценки и факта не совпадают."""

    def __init__(self) -> None:
        super().__init__(
            rule="EffortUnitMatch",
            message="Единицы оценки и факта не совпадают",
        )


class InvalidEffortValueException(BusinessRuleViolationException):
    """Некорректное значение усилия."""

    def __init__(self, detail: str = "") -> None:
        super().__init__(
            rule="ValidEffortValue",
            message=f"Некорректное значение усилия{f': {detail}' if detail else ''}",
        )


class RecurringTaskConfigurationException(BusinessRuleViolationException):
    """Некорректная конфигурация повторения."""

    def __init__(self, detail: str = "") -> None:
        super().__init__(
            rule="ValidRecurrenceConfig",
            message=f"Некорректная конфигурация повторения{f': {detail}' if detail else ''}",
        )


class AttachmentNotFoundException(EntityNotFoundException):
    """Вложение не найдено."""

    def __init__(self, id: object) -> None:
        super().__init__(entity_type="TaskAttachment", id=id)
