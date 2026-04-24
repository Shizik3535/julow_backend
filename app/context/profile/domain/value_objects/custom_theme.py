from __future__ import annotations

from dataclasses import dataclass, field

from app.shared.domain.base_value_object import ValueObject
from app.shared.domain.value_objects.color_vo import Color


@dataclass(frozen=True)
class CustomTheme(ValueObject):
    """
    Пользовательская тема оформления.

    Активируется при Theme.CUSTOM в AppearanceSettings.
    Содержит имя и словарь цветов по ролям (background, surface, text, primary, etc.).

    Атрибуты:
        name: Название темы.
        colors: Словарь цветов по ролям (ключ — роль, значение — Color).
    """

    name: str
    colors: dict[str, Color] = field(default_factory=dict)
