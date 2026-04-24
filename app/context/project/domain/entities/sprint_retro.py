from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.shared.domain.base_entity import BaseEntity
from app.shared.domain.value_objects.id_vo import Id
from app.context.project.domain.value_objects.retro_section import RetroSection
from app.context.project.domain.entities.retro_item import RetroItem


@dataclass
class SprintRetro(BaseEntity):
    """
    Сущность ретроспективы спринта.

    Принадлежит агрегату Sprint.

    Атрибуты:
        template_name: Название шаблона.
        sections: Секции ретроспективы.
        items: Элементы ретроспективы.
        created_at: Время создания.
    """

    template_name: str = ""
    sections: list[RetroSection] = field(default_factory=list)
    items: list[RetroItem] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
