from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.shared.domain.base_entity import BaseEntity
from app.shared.domain.value_objects.id_vo import Id
from app.context.profile.domain.value_objects.pinned_target_type import PinnedTargetType


@dataclass
class PinnedItem(BaseEntity):
    """
    Закреплённый элемент.

    Атрибуты:
        target_type: Тип закреплённого элемента.
        target_id: ID целевого объекта (opaque, из другого BC).
        order: Порядок закреплённого элемента.
        pinned_at: Время закрепления.
    """

    target_type: PinnedTargetType = PinnedTargetType.TASK
    target_id: Id = field(default_factory=Id.generate)
    order: int = 0
    pinned_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
