from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import date, datetime, timezone

from app.shared.domain.base_aggregate import AggregateRoot
from app.shared.domain.value_objects.id_vo import Id
from app.shared.domain.value_objects.money_vo import Money
from app.context.timetracking.domain.value_objects.timer_state import TimerState
from app.context.timetracking.domain.value_objects.time_entry_status import TimeEntryStatus
from app.context.timetracking.domain.value_objects.duration import Duration
from app.context.timetracking.domain.value_objects.time_rounding_config import TimeRoundingConfig
from app.context.timetracking.domain.value_objects.time_rounding_rule import TimeRoundingRule
from app.context.timetracking.domain.value_objects.rounding_apply_to import RoundingApplyTo
from app.context.timetracking.domain.entities.time_log import TimeLog
from app.context.timetracking.domain.entities.rejection_reason import RejectionReason
from app.context.timetracking.domain.events.time_entry_events import (
    TimerStarted,
    TimerPaused,
    TimerResumed,
    TimerStopped,
    TimeEntryCreated,
    TimeEntryUpdated,
    TimeEntryDeleted,
    TimeEntrySubmitted,
    TimeEntryApproved,
    TimeEntryRejected,
    TimeEntryLocked,
    TimeEntryCategoryChanged,
    TimeEntryBillableChanged,
    TimeEntryTagAdded,
    TimeEntryTagRemoved,
)
from app.context.timetracking.domain.exceptions.time_entry_exceptions import (
    TimerAlreadyRunningException,
    TimerNotRunningException,
    TimerNotPausedException,
    CannotDeleteNonDraftTimeEntryException,
    CannotEditLockedTimeEntryException,
    CannotEditApprovedTimeEntryException,
    CannotApproveOwnTimeEntryException,
    CannotSetHourlyRateForNonBillableException,
    TimeEntryAlreadySubmittedException,
    TimeEntryAlreadyApprovedException,
    TimeEntryNotSubmittedException,
    InvalidTimeEntryDurationException,
)


def _apply_rounding(seconds: int, rule: TimeRoundingRule) -> int:
    """Применяет правило округления к количеству секунд."""
    if rule == TimeRoundingRule.NONE:
        return seconds
    if rule == TimeRoundingRule.ROUND_UP_15:
        interval = 15 * 60
        return math.ceil(seconds / interval) * interval
    if rule == TimeRoundingRule.ROUND_UP_30:
        interval = 30 * 60
        return math.ceil(seconds / interval) * interval
    if rule == TimeRoundingRule.ROUND_NEAREST_15:
        interval = 15 * 60
        return round(seconds / interval) * interval
    if rule == TimeRoundingRule.ROUND_NEAREST_30:
        interval = 30 * 60
        return round(seconds / interval) * interval
    return seconds


@dataclass
class TimeEntry(AggregateRoot):
    """
    Корень агрегата записи времени (TimeTracking BC).

    Поддерживает таймер (start/stop/pause) и ручной ввод.
    Workflow утверждения: DRAFT → SUBMITTED → APPROVED/REJECTED → LOCKED.

    Атрибуты:
        user_id: ID пользователя.
        task_id: Opaque ID задачи (из Task BC).
        project_id: Opaque ID проекта (из Project BC).
        epic_id: Opaque ID эпика (из Project BC).
        workspace_id: Opaque ID workspace.
        description: Описание.
        timer_state: Состояние таймера.
        status: Статус записи.
        started_at: Время старта таймера.
        stopped_at: Время остановки таймера.
        duration: Длительность.
        entry_date: Дата записи.
        is_billable: Оплачиваемая ли.
        hourly_rate: Почасовая ставка.
        category_id: ID категории деятельности.
        tag_ids: Список ID тегов.
        time_logs: Детализация таймера.
        rejection_reason: Причина отклонения.
        rounding_config: Конфигурация округления.
        created_at: Время создания.
        updated_at: Время последнего обновления.
    """

    user_id: Id = field(kw_only=True)
    task_id: Id | None = None
    project_id: Id | None = None
    epic_id: Id | None = None
    workspace_id: Id = field(kw_only=True)
    description: str | None = None
    timer_state: TimerState = TimerState.STOPPED
    status: TimeEntryStatus = TimeEntryStatus.DRAFT
    started_at: datetime | None = None
    stopped_at: datetime | None = None
    duration: Duration = field(default_factory=lambda: Duration(seconds=0))
    entry_date: date = field(default_factory=date.today)
    is_billable: bool = False
    hourly_rate: Money | None = None
    category_id: Id | None = None
    tag_ids: list[Id] = field(default_factory=list)
    time_logs: list[TimeLog] = field(default_factory=list)
    rejection_reason: RejectionReason | None = None
    rounding_config: TimeRoundingConfig | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))

    # --- Фабричные методы ---

    @classmethod
    def create_manual(
        cls,
        user_id: Id,
        duration: Duration,
        entry_date: date,
        workspace_id: Id,
        task_id: Id | None = None,
        project_id: Id | None = None,
        epic_id: Id | None = None,
        description: str | None = None,
        is_billable: bool = False,
        hourly_rate: Money | None = None,
        category_id: Id | None = None,
    ) -> TimeEntry:
        """Создаёт запись ручного ввода."""
        if duration.seconds <= 0:
            raise InvalidTimeEntryDurationException(detail="длительность должна быть > 0")
        entry = cls(
            user_id=user_id,
            duration=duration,
            entry_date=entry_date,
            workspace_id=workspace_id,
            task_id=task_id,
            project_id=project_id,
            epic_id=epic_id,
            description=description,
            is_billable=is_billable,
            hourly_rate=hourly_rate,
            category_id=category_id,
            timer_state=TimerState.STOPPED,
            status=TimeEntryStatus.DRAFT,
        )
        entry._register_event(
            TimeEntryCreated(
                entry_id=str(entry.id),
                user_id=str(user_id),
                entry_date=str(entry_date),
                duration_seconds=duration.seconds,
            )
        )
        return entry

    @classmethod
    def create_for_timer(
        cls,
        user_id: Id,
        workspace_id: Id,
        entry_date: date,
        description: str | None = None,
        task_id: Id | None = None,
        project_id: Id | None = None,
        epic_id: Id | None = None,
    ) -> TimeEntry:
        """Создаёт запись для запуска таймера (duration=0, статус DRAFT)."""
        entry = cls(
            user_id=user_id,
            workspace_id=workspace_id,
            description=description,
            duration=Duration(seconds=0),
            entry_date=entry_date,
            task_id=task_id,
            project_id=project_id,
            epic_id=epic_id,
            timer_state=TimerState.STOPPED,
            status=TimeEntryStatus.DRAFT,
        )
        entry._register_event(
            TimeEntryCreated(
                entry_id=str(entry.id),
                user_id=str(user_id),
                entry_date=str(entry_date),
                duration_seconds=0,
            )
        )
        return entry

    # --- Инварианты ---

    def _assert_can_edit(self) -> None:
        if self.status == TimeEntryStatus.LOCKED:
            raise CannotEditLockedTimeEntryException()
        if self.status == TimeEntryStatus.APPROVED:
            raise CannotEditApprovedTimeEntryException()
        if self.status == TimeEntryStatus.SUBMITTED:
            raise TimeEntryAlreadySubmittedException()

    # --- Таймер ---

    def start_timer(self, task_id: Id | None = None, project_id: Id | None = None, epic_id: Id | None = None) -> None:
        """Запускает таймер: STOPPED → RUNNING."""
        self._assert_can_edit()
        if self.timer_state == TimerState.RUNNING:
            raise TimerAlreadyRunningException()
        now = datetime.now(tz=timezone.utc)
        self.timer_state = TimerState.RUNNING
        self.started_at = now
        self.task_id = task_id
        self.project_id = project_id
        self.epic_id = epic_id
        self.time_logs.append(TimeLog(action=TimerState.RUNNING, timestamp=now, accumulated_seconds=0))
        self.updated_at = now
        self._register_event(
            TimerStarted(
                entry_id=str(self.id),
                user_id=str(self.user_id),
                task_id=str(task_id) if task_id else "",
                project_id=str(project_id) if project_id else "",
            )
        )

    def pause_timer(self) -> None:
        """Приостанавливает таймер: RUNNING → PAUSED."""
        if self.timer_state != TimerState.RUNNING:
            raise TimerNotRunningException()
        now = datetime.now(tz=timezone.utc)
        accumulated = self._compute_accumulated_seconds(now)
        self.timer_state = TimerState.PAUSED
        self.time_logs.append(TimeLog(action=TimerState.PAUSED, timestamp=now, accumulated_seconds=accumulated))
        self.updated_at = now
        self._register_event(
            TimerPaused(entry_id=str(self.id), accumulated_seconds=accumulated)
        )

    def resume_timer(self) -> None:
        """Возобновляет таймер: PAUSED → RUNNING."""
        if self.timer_state != TimerState.PAUSED:
            raise TimerNotPausedException()
        now = datetime.now(tz=timezone.utc)
        accumulated = self._compute_accumulated_seconds(now)
        self.timer_state = TimerState.RUNNING
        self.time_logs.append(TimeLog(action=TimerState.RUNNING, timestamp=now, accumulated_seconds=accumulated))
        self.updated_at = now
        self._register_event(TimerResumed(entry_id=str(self.id)))

    def stop_timer(self) -> None:
        """Останавливает таймер: RUNNING/PAUSED → STOPPED, подсчёт duration."""
        if self.timer_state == TimerState.STOPPED:
            raise TimerNotRunningException()
        now = datetime.now(tz=timezone.utc)
        accumulated = self._compute_accumulated_seconds(now)
        self.timer_state = TimerState.STOPPED
        self.stopped_at = now
        self.time_logs.append(TimeLog(action=TimerState.STOPPED, timestamp=now, accumulated_seconds=accumulated))
        # Применяем округление
        rounded = accumulated
        if self.rounding_config is not None and self.rounding_config.apply_to != RoundingApplyTo.MANUAL_ONLY:
            rounded = _apply_rounding(accumulated, self.rounding_config.rule)
        self.duration = Duration(seconds=rounded)
        self.updated_at = now
        self._register_event(
            TimerStopped(entry_id=str(self.id), duration_seconds=rounded)
        )

    def _compute_accumulated_seconds(self, now: datetime) -> int:
        """Вычисляет накопленное время из time_logs."""
        total = 0
        running_from: datetime | None = None
        for log in self.time_logs:
            if log.action == TimerState.RUNNING:
                running_from = log.timestamp
            elif log.action == TimerState.PAUSED and running_from is not None:
                total += int((log.timestamp - running_from).total_seconds())
                running_from = None
            elif log.action == TimerState.STOPPED and running_from is not None:
                total += int((log.timestamp - running_from).total_seconds())
                running_from = None
        # Если сейчас RUNNING, добавляем время от последнего старта
        if self.timer_state == TimerState.RUNNING and running_from is not None:
            total += int((now - running_from).total_seconds())
        return total

    # --- Обновление ---

    def update(
        self,
        description: str | None = None,
        is_billable: bool | None = None,
        hourly_rate: Money | None = None,
        category_id: Id | None = None,
    ) -> None:
        """Обновляет запись (только если DRAFT)."""
        self._assert_can_edit()
        changed: list[str] = []
        if description is not None and self.description != description:
            self.description = description
            changed.append("description")
        if is_billable is not None and self.is_billable != is_billable:
            self.is_billable = is_billable
            if not is_billable:
                self.hourly_rate = None
            changed.append("is_billable")
            self._register_event(
                TimeEntryBillableChanged(entry_id=str(self.id), is_billable=is_billable)
            )
        if hourly_rate is not None and self.is_billable:
            self.hourly_rate = hourly_rate
            changed.append("hourly_rate")
        elif hourly_rate is not None and not self.is_billable:
            raise CannotSetHourlyRateForNonBillableException()
        if category_id is not None and self.category_id != category_id:
            self.category_id = category_id
            changed.append("category_id")
        if changed:
            self.updated_at = datetime.now(tz=timezone.utc)
            self._register_event(
                TimeEntryUpdated(entry_id=str(self.id), changed_fields=changed)
            )

    def set_task(self, task_id: Id) -> None:
        self._assert_can_edit()
        self.task_id = task_id
        self.updated_at = datetime.now(tz=timezone.utc)

    def set_project(self, project_id: Id) -> None:
        self._assert_can_edit()
        self.project_id = project_id
        self.updated_at = datetime.now(tz=timezone.utc)

    def set_epic(self, epic_id: Id) -> None:
        self._assert_can_edit()
        self.epic_id = epic_id
        self.updated_at = datetime.now(tz=timezone.utc)

    # --- Теги ---

    def add_tag(self, tag_id: Id) -> None:
        self._assert_can_edit()
        if tag_id not in self.tag_ids:
            self.tag_ids.append(tag_id)
            self.updated_at = datetime.now(tz=timezone.utc)
            self._register_event(
                TimeEntryTagAdded(entry_id=str(self.id), tag_id=str(tag_id))
            )

    def remove_tag(self, tag_id: Id) -> None:
        self._assert_can_edit()
        if tag_id in self.tag_ids:
            self.tag_ids = [t for t in self.tag_ids if t != tag_id]
            self.updated_at = datetime.now(tz=timezone.utc)
            self._register_event(
                TimeEntryTagRemoved(entry_id=str(self.id), tag_id=str(tag_id))
            )

    # --- Workflow утверждения ---

    def submit(self) -> None:
        """DRAFT → SUBMITTED."""
        if self.status != TimeEntryStatus.DRAFT:
            raise TimeEntryAlreadySubmittedException()
        self.status = TimeEntryStatus.SUBMITTED
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            TimeEntrySubmitted(entry_id=str(self.id), user_id=str(self.user_id))
        )

    def approve(self, approved_by: Id) -> None:
        """SUBMITTED → APPROVED."""
        if approved_by == self.user_id:
            raise CannotApproveOwnTimeEntryException()
        if self.status != TimeEntryStatus.SUBMITTED:
            raise TimeEntryAlreadyApprovedException()
        self.status = TimeEntryStatus.APPROVED
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            TimeEntryApproved(entry_id=str(self.id), approved_by=str(approved_by))
        )

    def reject(self, rejected_by: Id, reason: str) -> None:
        """SUBMITTED → REJECTED."""
        if self.status != TimeEntryStatus.SUBMITTED:
            raise TimeEntryNotSubmittedException()
        self.status = TimeEntryStatus.REJECTED
        self.rejection_reason = RejectionReason(reason=reason, rejected_by=rejected_by)
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            TimeEntryRejected(entry_id=str(self.id), rejected_by=str(rejected_by), reason=reason)
        )

    def resubmit(self) -> None:
        """REJECTED → SUBMITTED."""
        if self.status != TimeEntryStatus.REJECTED:
            raise TimeEntryAlreadySubmittedException()
        self.status = TimeEntryStatus.SUBMITTED
        self.rejection_reason = None
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            TimeEntrySubmitted(entry_id=str(self.id), user_id=str(self.user_id))
        )

    def lock(self) -> None:
        """→ LOCKED (app-layer handler при закрытии периода)."""
        self.status = TimeEntryStatus.LOCKED
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(TimeEntryLocked(entry_id=str(self.id)))

    def delete(self) -> None:
        """Удаление (только если DRAFT)."""
        if self.status != TimeEntryStatus.DRAFT:
            raise CannotDeleteNonDraftTimeEntryException()
        self._register_event(TimeEntryDeleted(entry_id=str(self.id)))
