from __future__ import annotations

from dataclasses import dataclass

from app.shared.domain.base_entity import BaseEntity
from app.shared.domain.value_objects.color_vo import Color


@dataclass
class FileTag(BaseEntity):
    """
    Сущность тега/метки файла.

    Принадлежит агрегату File. Уникален по имени в рамках файла.

    Атрибуты:
        name: Название тега.
        color: Цвет тега (из shared kernel).
    """

    name: str = ""
    color: Color | None = None
