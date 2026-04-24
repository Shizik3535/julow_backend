from __future__ import annotations

from app.shared.domain.base_exceptions import DomainException
from app.shared.domain.exceptions import BusinessRuleViolationException, EntityNotFoundException


class BoardColumnNotFoundException(EntityNotFoundException):
    """Колонка не найдена."""

    def __init__(self, id: object) -> None:
        super().__init__(entity_type="BoardColumn", id=id)


class SwimlaneNotFoundException(EntityNotFoundException):
    """Swimlane не найдена."""

    def __init__(self, id: object) -> None:
        super().__init__(entity_type="Swimlane", id=id)


class WorkflowStatusNotFoundException(EntityNotFoundException):
    """Статус workflow не найден."""

    def __init__(self, id: object) -> None:
        super().__init__(entity_type="WorkflowStatus", id=id)


class WorkflowTransitionNotAllowedException(BusinessRuleViolationException):
    """Переход не разрешён."""

    def __init__(self, reason: str = "") -> None:
        super().__init__(
            rule="WorkflowTransitionNotAllowed",
            message=f"Переход не разрешён{f': {reason}' if reason else ''}",
        )


class CircularTransitionException(BusinessRuleViolationException):
    """Циклический переход."""

    def __init__(self) -> None:
        super().__init__(
            rule="NoCircularTransition",
            message="Циклический переход в workflow",
        )


class WIPLimitExceededException(BusinessRuleViolationException):
    """WIP-лимит превышен."""

    def __init__(self, column_name: str = "") -> None:
        super().__init__(
            rule="WIPLimit",
            message=f"WIP-лимит превышен{f': {column_name}' if column_name else ''}",
        )
