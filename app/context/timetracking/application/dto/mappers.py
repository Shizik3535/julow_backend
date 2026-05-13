"""Helper-маппинги доменных агрегатов в DTO."""
from __future__ import annotations

from app.context.timetracking.application.dto.activity_category_dto import ActivityCategoryDTO
from app.context.timetracking.application.dto.time_entry_dto import TimeEntryDTO
from app.context.timetracking.application.dto.time_entry_tag_dto import TimeEntryTagDTO
from app.context.timetracking.domain.aggregates.activity_category import ActivityCategory
from app.context.timetracking.domain.aggregates.time_entry import TimeEntry
from app.context.timetracking.domain.aggregates.time_entry_tag import TimeEntryTag


def time_entry_to_dto(entry: TimeEntry) -> TimeEntryDTO:
    """Маппинг TimeEntry → TimeEntryDTO."""
    hourly_rate: dict | None = None
    if entry.hourly_rate is not None:
        hourly_rate = {
            "amount": str(entry.hourly_rate.amount),
            "currency": entry.hourly_rate.currency,
        }
    rounding_config: dict | None = None
    if entry.rounding_config is not None:
        rounding_config = {
            "rule": entry.rounding_config.rule.value,
            "apply_to": entry.rounding_config.apply_to.value,
        }
    rejection: dict | None = None
    if entry.rejection_reason is not None:
        rejection = {
            "reason": entry.rejection_reason.reason,
            "rejected_by": str(entry.rejection_reason.rejected_by),
            "rejected_at": entry.rejection_reason.rejected_at.isoformat(),
        }
    time_logs = [
        {
            "action": log.action.value,
            "timestamp": log.timestamp.isoformat(),
            "accumulated_seconds": log.accumulated_seconds,
        }
        for log in entry.time_logs
    ]
    return TimeEntryDTO(
        id=str(entry.id),
        user_id=str(entry.user_id),
        workspace_id=str(entry.workspace_id),
        task_id=str(entry.task_id) if entry.task_id else None,
        project_id=str(entry.project_id) if entry.project_id else None,
        epic_id=str(entry.epic_id) if entry.epic_id else None,
        description=entry.description,
        timer_state=entry.timer_state.value,
        status=entry.status.value,
        started_at=entry.started_at,
        stopped_at=entry.stopped_at,
        duration_seconds=entry.duration.seconds,
        entry_date=str(entry.entry_date),
        is_billable=entry.is_billable,
        hourly_rate=hourly_rate,
        category_id=str(entry.category_id) if entry.category_id else None,
        tag_ids=[str(t) for t in entry.tag_ids],
        time_logs=time_logs,
        rejection_reason=rejection,
        rounding_config=rounding_config,
        created_at=entry.created_at,
        updated_at=entry.updated_at,
    )


def category_to_dto(category: ActivityCategory) -> ActivityCategoryDTO:
    """Маппинг ActivityCategory → ActivityCategoryDTO."""
    return ActivityCategoryDTO(
        id=str(category.id),
        workspace_id=str(category.workspace_id) if category.workspace_id else None,
        name=category.name,
        color=category.color.value if category.color else None,
        is_system=category.is_system,
        description=category.description,
        is_deleted=category.is_deleted,
        created_at=category.created_at,
        updated_at=category.updated_at,
    )


def tag_to_dto(tag: TimeEntryTag) -> TimeEntryTagDTO:
    """Маппинг TimeEntryTag → TimeEntryTagDTO."""
    return TimeEntryTagDTO(
        id=str(tag.id),
        workspace_id=str(tag.workspace_id),
        name=tag.name,
        color=tag.color.value if tag.color else None,
        is_deleted=tag.is_deleted,
        created_at=tag.created_at,
        updated_at=tag.updated_at,
    )
