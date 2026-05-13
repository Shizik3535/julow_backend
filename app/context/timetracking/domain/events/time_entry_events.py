from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from app.shared.domain.base_domain_event import BaseDomainEvent
from app.context.timetracking.domain.value_objects.duration import Duration
from app.context.timetracking.domain.value_objects.time_entry_status import TimeEntryStatus


@dataclass(frozen=True)
class TimerStarted(BaseDomainEvent):
    """Таймер запущен."""

    entry_id: str = ""
    user_id: str = ""
    task_id: str = ""
    project_id: str = ""


@dataclass(frozen=True)
class TimerPaused(BaseDomainEvent):
    """Таймер приостановлен."""

    entry_id: str = ""
    accumulated_seconds: int = 0


@dataclass(frozen=True)
class TimerResumed(BaseDomainEvent):
    """Таймер возобновлён."""

    entry_id: str = ""


@dataclass(frozen=True)
class TimerStopped(BaseDomainEvent):
    """Таймер остановлен."""

    entry_id: str = ""
    duration_seconds: int = 0


@dataclass(frozen=True)
class TimeEntryCreated(BaseDomainEvent):
    """Запись времени создана (ручной ввод)."""

    entry_id: str = ""
    user_id: str = ""
    entry_date: str = ""
    duration_seconds: int = 0


@dataclass(frozen=True)
class TimeEntryUpdated(BaseDomainEvent):
    """Запись обновлена."""

    entry_id: str = ""
    changed_fields: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class TimeEntryDeleted(BaseDomainEvent):
    """Запись удалена."""

    entry_id: str = ""


@dataclass(frozen=True)
class TimeEntrySubmitted(BaseDomainEvent):
    """Запись отправлена на утверждение."""

    entry_id: str = ""
    user_id: str = ""


@dataclass(frozen=True)
class TimeEntryApproved(BaseDomainEvent):
    """Запись утверждена."""

    entry_id: str = ""
    approved_by: str = ""


@dataclass(frozen=True)
class TimeEntryRejected(BaseDomainEvent):
    """Запись отклонена."""

    entry_id: str = ""
    rejected_by: str = ""
    reason: str = ""


@dataclass(frozen=True)
class TimeEntryLocked(BaseDomainEvent):
    """Запись заблокирована (период закрыт)."""

    entry_id: str = ""


@dataclass(frozen=True)
class TimeEntryCategoryChanged(BaseDomainEvent):
    """Категория изменена."""

    entry_id: str = ""
    category_name: str = ""


@dataclass(frozen=True)
class TimeEntryBillableChanged(BaseDomainEvent):
    """Billable статус изменён."""

    entry_id: str = ""
    is_billable: bool = False


@dataclass(frozen=True)
class TimeEntryTagAdded(BaseDomainEvent):
    """Тег добавлен."""

    entry_id: str = ""
    tag_id: str = ""


@dataclass(frozen=True)
class TimeEntryTagRemoved(BaseDomainEvent):
    """Тег удалён."""

    entry_id: str = ""
    tag_id: str = ""


@dataclass(frozen=True)
class TimeEntryTagDeleted(BaseDomainEvent):
    """Тег записи времени удалён (soft delete)."""

    tag_id: str = ""
    workspace_id: str = ""


@dataclass(frozen=True)
class UnfilledTimeReminderTriggered(BaseDomainEvent):
    """Напоминание о незаполненном времени."""

    user_id: str = ""
    entry_date: str = ""


@dataclass(frozen=True)
class TimePeriodLocked(BaseDomainEvent):
    """Период времени заблокирован."""

    workspace_id: str = ""
    period_start: str = ""
    period_end: str = ""
