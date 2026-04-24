from __future__ import annotations

from dataclasses import dataclass

from app.shared.domain.base_value_object import ValueObject
from app.context.project.domain.value_objects.retro_item_type import RetroItemType


@dataclass(frozen=True)
class RetroSection(ValueObject):
    """
    Value Object для секции шаблона ретроспективы.

    Атрибуты:
        title: Заголовок секции.
        prompt: Подсказка для участников (None — без подсказки).
        item_type: Тип элементов в секции.
    """

    title: str
    prompt: str | None = None
    item_type: RetroItemType = RetroItemType.NEUTRAL
