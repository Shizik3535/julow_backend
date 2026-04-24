from __future__ import annotations

from dataclasses import dataclass, field

from app.shared.domain.base_value_object import ValueObject
from app.context.profile.domain.value_objects.start_page import StartPage


@dataclass(frozen=True)
class NavigationSettings(ValueObject):
    """
    Группа настроек навигации.

    Атрибуты:
        start_page: Идентификатор стартовой страницы.
    """

    start_page: StartPage = field(default_factory=lambda: StartPage("dashboard"))
