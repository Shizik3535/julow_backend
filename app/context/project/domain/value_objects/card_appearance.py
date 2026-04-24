from __future__ import annotations

from dataclasses import dataclass, field

from app.shared.domain.base_value_object import ValueObject


@dataclass(frozen=True)
class CardAppearance(ValueObject):
    """
    Настройки отображения карточки на доске.

    Атрибуты:
        visible_fields: Список имён полей для отображения.
        compact_mode: Компактный режим.
        show_cover_image: Показывать обложку.
    """

    visible_fields: list[str] = field(default_factory=list)
    compact_mode: bool = False
    show_cover_image: bool = True
