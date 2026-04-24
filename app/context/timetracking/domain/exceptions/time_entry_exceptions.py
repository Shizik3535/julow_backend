from __future__ import annotations

from app.shared.domain.base_exceptions import DomainException
from app.shared.domain.exceptions import BusinessRuleViolationException, EntityNotFoundException


class TimeEntryNotFoundException(EntityNotFoundException):
    """Запись времени не найдена."""

    def __init__(self, id: object) -> None:
        super().__init__(entity_type="TimeEntry", id=id)


class TimerAlreadyRunningException(BusinessRuleViolationException):
    """У пользователя уже есть запущенный таймер."""

    def __init__(self) -> None:
        super().__init__(
            rule="SingleActiveTimer",
            message="У пользователя уже есть запущенный таймер",
        )


class TimerNotRunningException(DomainException):
    """Таймер не запущен."""

    def __init__(self) -> None:
        super().__init__("Таймер не запущен")


class TimerNotPausedException(DomainException):
    """Таймер не на паузе."""

    def __init__(self) -> None:
        super().__init__("Таймер не на паузе (нельзя возобновить)")


class CannotEditLockedTimeEntryException(BusinessRuleViolationException):
    """Нельзя редактировать заблокированную запись."""

    def __init__(self) -> None:
        super().__init__(
            rule="CanEditTimeEntry",
            message="Нельзя редактировать заблокированную запись",
        )


class CannotEditApprovedTimeEntryException(BusinessRuleViolationException):
    """Нельзя редактировать утверждённую запись."""

    def __init__(self) -> None:
        super().__init__(
            rule="CanEditTimeEntry",
            message="Нельзя редактировать утверждённую запись",
        )


class CannotSubmitDraftTimeEntryException(BusinessRuleViolationException):
    """Нельзя отправить черновик без обязательных полей."""

    def __init__(self, reason: str = "") -> None:
        super().__init__(
            rule="CanSubmitTimeEntry",
            message=f"Нельзя отправить черновик без обязательных полей{f': {reason}' if reason else ''}",
        )


class CannotApproveOwnTimeEntryException(BusinessRuleViolationException):
    """Нельзя утвердить свою же запись."""

    def __init__(self) -> None:
        super().__init__(
            rule="CannotApproveOwn",
            message="Нельзя утвердить свою же запись",
        )


class TimeEntryAlreadySubmittedException(BusinessRuleViolationException):
    """Запись уже отправлена на утверждение."""

    def __init__(self) -> None:
        super().__init__(
            rule="TimeEntryNotAlreadySubmitted",
            message="Запись уже отправлена на утверждение",
        )


class TimeEntryAlreadyApprovedException(BusinessRuleViolationException):
    """Запись уже утверждена."""

    def __init__(self) -> None:
        super().__init__(
            rule="TimeEntryNotAlreadyApproved",
            message="Запись уже утверждена",
        )


class InvalidTimeEntryDurationException(BusinessRuleViolationException):
    """Некорректная длительность."""

    def __init__(self, detail: str = "") -> None:
        super().__init__(
            rule="ValidDuration",
            message=f"Некорректная длительность{f': {detail}' if detail else ''}",
        )


class DuplicateTimerException(BusinessRuleViolationException):
    """Только один активный таймер на пользователя."""

    def __init__(self) -> None:
        super().__init__(
            rule="SingleActiveTimer",
            message="Только один активный таймер на пользователя",
        )


class TimePeriodLockedException(DomainException):
    """Период заблокирован."""

    def __init__(self) -> None:
        super().__init__("Период заблокирован, нельзя добавлять/редактировать записи")
