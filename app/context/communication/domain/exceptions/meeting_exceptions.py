from __future__ import annotations

from app.shared.domain.base_exceptions import DomainException
from app.shared.domain.exceptions import BusinessRuleViolationException, EntityNotFoundException


class MeetingNotFoundException(EntityNotFoundException):
    """Совещание не найдено."""

    def __init__(self, id: object) -> None:
        super().__init__(entity_type="Meeting", id=id)


class CannotAddMeetingNoteException(BusinessRuleViolationException):
    """Заметку можно добавить только к начатому/завершённому совещанию."""

    def __init__(self) -> None:
        super().__init__(
            rule="MeetingNoteOnlyInProgressOrCompleted",
            message="Заметку можно добавить только к начатому/завершённому совещанию",
        )


class MeetingAlreadyStartedException(BusinessRuleViolationException):
    """Совещание уже начато."""

    def __init__(self) -> None:
        super().__init__(
            rule="MeetingNotAlreadyStarted",
            message="Совещание уже начато",
        )


class MeetingAlreadyCompletedException(BusinessRuleViolationException):
    """Совещание уже завершено."""

    def __init__(self) -> None:
        super().__init__(
            rule="MeetingNotAlreadyCompleted",
            message="Совещание уже завершено",
        )


class InvalidRSVPStatusTransitionException(BusinessRuleViolationException):
    """Некорректный переход RSVP статуса."""

    def __init__(self, from_status: str = "", to_status: str = "") -> None:
        super().__init__(
            rule="ValidRSVPTransition",
            message=f"Некорректный переход RSVP: {from_status} → {to_status}",
        )


class MeetingActionItemNotFoundException(EntityNotFoundException):
    """Action item не найден."""

    def __init__(self, id: object) -> None:
        super().__init__(entity_type="MeetingActionItem", id=id)


class RecurringMeetingConfigurationException(BusinessRuleViolationException):
    """Некорректная конфигурация повторения."""

    def __init__(self, detail: str = "") -> None:
        super().__init__(
            rule="ValidRecurrenceConfig",
            message=f"Некорректная конфигурация повторения{f': {detail}' if detail else ''}",
        )
