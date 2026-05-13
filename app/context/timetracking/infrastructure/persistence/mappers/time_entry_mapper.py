from __future__ import annotations

from decimal import Decimal

from app.shared.domain.value_objects.id_vo import Id
from app.shared.domain.value_objects.money_vo import Money
from app.shared.infrastructure.persistence.sqlalchemy_base_mapper import BaseMapper

from app.context.timetracking.domain.aggregates.time_entry import TimeEntry
from app.context.timetracking.domain.entities.rejection_reason import RejectionReason
from app.context.timetracking.domain.entities.time_log import TimeLog
from app.context.timetracking.domain.value_objects.duration import Duration
from app.context.timetracking.domain.value_objects.rounding_apply_to import RoundingApplyTo
from app.context.timetracking.domain.value_objects.time_entry_status import TimeEntryStatus
from app.context.timetracking.domain.value_objects.time_rounding_config import TimeRoundingConfig
from app.context.timetracking.domain.value_objects.time_rounding_rule import TimeRoundingRule
from app.context.timetracking.domain.value_objects.timer_state import TimerState
from app.context.timetracking.infrastructure.persistence.orm_models.time_entry_orm import (
    TimeEntryORM,
    TimeEntryTimeLogORM,
)


class TimeEntryMapper(BaseMapper[TimeEntry, TimeEntryORM]):
    """Data Mapper: TimeEntry ↔ TimeEntryORM."""

    # ------------------------------------------------------------------
    # ORM → Domain
    # ------------------------------------------------------------------

    def to_domain(self, orm_model: TimeEntryORM) -> TimeEntry:
        hourly_rate: Money | None = None
        if orm_model.hourly_rate_amount is not None and orm_model.hourly_rate_currency:
            hourly_rate = Money(
                amount=Decimal(orm_model.hourly_rate_amount),
                currency=orm_model.hourly_rate_currency,
            )

        rounding_config: TimeRoundingConfig | None = None
        if orm_model.rounding_rule is not None and orm_model.rounding_apply_to is not None:
            rounding_config = TimeRoundingConfig(
                rule=TimeRoundingRule(orm_model.rounding_rule),
                apply_to=RoundingApplyTo(orm_model.rounding_apply_to),
            )

        rejection: RejectionReason | None = None
        if orm_model.rejection_reason_text and orm_model.rejected_by:
            rejection = RejectionReason(
                reason=orm_model.rejection_reason_text,
                rejected_by=self._map_id(orm_model.rejected_by),
                rejected_at=orm_model.rejected_at,  # type: ignore[arg-type]
            )

        # tag_ids — загружаются отдельно через ассоциативную таблицу
        tag_ids: list[Id] = list(getattr(orm_model, "_loaded_tag_ids", []))

        time_logs = [
            TimeLog(
                id=self._map_id(log.id),
                action=TimerState(log.action),
                timestamp=log.timestamp,
                accumulated_seconds=log.accumulated_seconds,
            )
            for log in orm_model.time_logs
        ]

        return TimeEntry(
            id=self._map_id(orm_model.id),
            user_id=self._map_id(orm_model.user_id),
            workspace_id=self._map_id(orm_model.workspace_id),
            task_id=self._map_id(orm_model.task_id) if orm_model.task_id else None,
            project_id=self._map_id(orm_model.project_id) if orm_model.project_id else None,
            epic_id=self._map_id(orm_model.epic_id) if orm_model.epic_id else None,
            description=orm_model.description,
            timer_state=TimerState(orm_model.timer_state),
            status=TimeEntryStatus(orm_model.status),
            started_at=orm_model.started_at,
            stopped_at=orm_model.stopped_at,
            duration=Duration(seconds=orm_model.duration_seconds),
            entry_date=orm_model.entry_date,
            is_billable=orm_model.is_billable,
            hourly_rate=hourly_rate,
            category_id=self._map_id(orm_model.category_id) if orm_model.category_id else None,
            tag_ids=tag_ids,
            time_logs=time_logs,
            rejection_reason=rejection,
            rounding_config=rounding_config,
            created_at=orm_model.created_at,
            updated_at=orm_model.updated_at,
        )

    # ------------------------------------------------------------------
    # Domain → ORM
    # ------------------------------------------------------------------

    def to_orm(self, aggregate: TimeEntry) -> TimeEntryORM:
        hourly_amount = aggregate.hourly_rate.amount if aggregate.hourly_rate else None
        hourly_currency = aggregate.hourly_rate.currency if aggregate.hourly_rate else None

        rounding_rule = aggregate.rounding_config.rule.value if aggregate.rounding_config else None
        rounding_apply_to = (
            aggregate.rounding_config.apply_to.value if aggregate.rounding_config else None
        )

        rejection_text = aggregate.rejection_reason.reason if aggregate.rejection_reason else None
        rejected_by = (
            self._map_uuid(aggregate.rejection_reason.rejected_by)
            if aggregate.rejection_reason
            else None
        )
        rejected_at = aggregate.rejection_reason.rejected_at if aggregate.rejection_reason else None

        orm = TimeEntryORM(
            id=self._map_uuid(aggregate.id),
            user_id=self._map_uuid(aggregate.user_id),
            workspace_id=self._map_uuid(aggregate.workspace_id),
            task_id=self._map_uuid(aggregate.task_id) if aggregate.task_id else None,
            project_id=self._map_uuid(aggregate.project_id) if aggregate.project_id else None,
            epic_id=self._map_uuid(aggregate.epic_id) if aggregate.epic_id else None,
            description=aggregate.description,
            timer_state=aggregate.timer_state.value,
            status=aggregate.status.value,
            started_at=aggregate.started_at,
            stopped_at=aggregate.stopped_at,
            duration_seconds=aggregate.duration.seconds,
            entry_date=aggregate.entry_date,
            is_billable=aggregate.is_billable,
            hourly_rate_amount=hourly_amount,
            hourly_rate_currency=hourly_currency,
            category_id=self._map_uuid(aggregate.category_id) if aggregate.category_id else None,
            rounding_rule=rounding_rule,
            rounding_apply_to=rounding_apply_to,
            rejection_reason_text=rejection_text,
            rejected_by=rejected_by,
            rejected_at=rejected_at,
            created_at=aggregate.created_at,
            updated_at=aggregate.updated_at,
        )
        orm.time_logs = [self._time_log_to_orm(log, aggregate.id) for log in aggregate.time_logs]
        return orm

    def _time_log_to_orm(self, log: TimeLog, entry_id: Id) -> TimeEntryTimeLogORM:
        return TimeEntryTimeLogORM(
            id=self._map_uuid(log.id),
            time_entry_id=self._map_uuid(entry_id),
            action=log.action.value,
            timestamp=log.timestamp,
            accumulated_seconds=log.accumulated_seconds,
        )
