from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.shared.domain.base_entity import BaseEntity
from app.context.security.domain.value_objects.backup_type import BackupType
from app.context.security.domain.value_objects.backup_status import BackupStatus


@dataclass
class BackupRecord(BaseEntity):
    backup_type: BackupType = BackupType.FULL
    status: BackupStatus = BackupStatus.PENDING
    started_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
    completed_at: datetime | None = None
    size_bytes: int | None = None
    storage_path: str | None = None
    error_message: str | None = None
