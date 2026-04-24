from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.shared.domain.base_entity import BaseEntity
from app.shared.domain.value_objects.id_vo import Id
from app.context.task.domain.value_objects.relation_type import RelationType


@dataclass
class TaskRelation(BaseEntity):
    """
    Сущность связи с другой задачей.

    Принадлежит агрегату Task.

    Атрибуты:
        related_task_id: ID связанной задачи.
        relation_type: Тип связи.
        created_at: Время создания связи.
        created_by: ID создавшего связь.
    """

    related_task_id: Id = field(default_factory=Id.generate)
    relation_type: RelationType = RelationType.RELATES_TO
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
    created_by: Id = field(default_factory=Id.generate)
