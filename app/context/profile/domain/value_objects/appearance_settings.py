from __future__ import annotations

from dataclasses import dataclass, field

from app.shared.domain.base_value_object import ValueObject
from app.shared.domain.value_objects.color_vo import Color
from app.context.profile.domain.value_objects.theme import Theme
from app.context.profile.domain.value_objects.interface_density import InterfaceDensity
from app.context.profile.domain.value_objects.custom_theme import CustomTheme


@dataclass(frozen=True)
class AppearanceSettings(ValueObject):
    """
    Группа настроек внешнего вида.

    Атрибуты:
        theme: Тема оформления.
        accent_color: Акцентный цвет.
        custom_theme: Пользовательская тема (активна при Theme.CUSTOM).
        interface_density: Плотность интерфейса.
    """

    theme: Theme = Theme.SYSTEM
    accent_color: Color = field(default_factory=lambda: Color("#6366F1"))
    custom_theme: CustomTheme | None = None
    interface_density: InterfaceDensity = InterfaceDensity.COMFORTABLE
