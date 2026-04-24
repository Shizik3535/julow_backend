from __future__ import annotations

from dataclasses import dataclass, field

from app.shared.domain.base_value_object import ValueObject
from app.shared.domain.value_objects.id_vo import Id
from app.shared.domain.exceptions import ValidationException


@dataclass(frozen=True)
class SidebarSection(ValueObject):
    """
    Секция sidebar.

    Гибкая модель sidebar: произвольные секции с элементами,
    сворачиваемые, с порядком.

    Атрибуты:
        section_id: Идентификатор секции.
        is_collapsed: Свернута ли секция.
        item_ids: Список ID элементов внутри секции.
        order: Порядок секции в sidebar.
    """

    section_id: str = ""
    is_collapsed: bool = False
    item_ids: list[Id] = field(default_factory=list)
    order: int = 0

    def __post_init__(self) -> None:
        if not self.section_id.strip():
            raise ValidationException(
                field="section_id",
                message="Идентификатор секции не может быть пустым",
            )
