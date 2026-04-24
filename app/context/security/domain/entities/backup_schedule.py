from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.shared.domain.base_entity import BaseEntity
from app.context.security.domain.value_objects.backup_type import BackupType
from app.context.security.domain.value_objects.backup_frequency import BackupFrequency


@dataclass
class BackupSchedule(BaseEntity):
    backup_type: BackupType = BackupType.FULL
    frequency: BackupFrequency = BackupFrequency.DAILY
    retention_days: int = 90
    is_active: bool = True
    next_run_at: datetime | None = None
