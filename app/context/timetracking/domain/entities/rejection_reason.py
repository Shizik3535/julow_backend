from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.shared.domain.base_entity import BaseEntity
from app.shared.domain.value_objects.id_vo import Id


@dataclass
class RejectionReason(BaseEntity):
    """
    Сущность причины отклонения записи.

    Принадлежит агрегату TimeEntry.

    Атрибуты:
        reason: Текст причины.
        rejected_by: ID отклонившего.
        rejected_at: Время отклонения.
    """

    reason: str = ""
    rejected_by: Id = field(default_factory=Id.generate)
    rejected_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
