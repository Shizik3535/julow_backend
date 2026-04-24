from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.shared.domain.base_entity import BaseEntity
from app.shared.domain.value_objects.id_vo import Id


@dataclass
class IncidentNote(BaseEntity):
    author_id: Id = field(default_factory=Id.generate)
    content: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
