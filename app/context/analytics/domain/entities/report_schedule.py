from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.shared.domain.base_entity import BaseEntity
from app.shared.domain.value_objects.id_vo import Id
from app.context.analytics.domain.value_objects.report_frequency import ReportFrequency


@dataclass
class ReportSchedule(BaseEntity):
    """Сущность расписания отчёта."""

    frequency: ReportFrequency = ReportFrequency.WEEKLY
    recipients: list[Id] = field(default_factory=list)
    is_active: bool = True
    next_run_at: datetime | None = None
    last_run_at: datetime | None = None
