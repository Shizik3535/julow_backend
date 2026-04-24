from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.shared.domain.base_entity import BaseEntity
from app.shared.domain.value_objects.id_vo import Id


@dataclass
class FileLock(BaseEntity):
    """
    Сущность блокировки файла.

    Принадлежит агрегату File.

    Атрибуты:
        locked_by: ID заблокировавшего.
        locked_at: Время блокировки.
        expires_at: Время автоснятия (None — бессрочно).
        reason: Причина блокировки.
    """

    locked_by: Id = field(default_factory=Id.generate)
    locked_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
    expires_at: datetime | None = None
    reason: str | None = None
