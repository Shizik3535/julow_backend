from __future__ import annotations

from dataclasses import dataclass, field

from app.shared.domain.base_value_object import ValueObject
from app.context.project.domain.value_objects.view_type import ViewType
from app.context.project.domain.value_objects.view_filter import ViewFilter
from app.context.project.domain.value_objects.sort_rule import SortRule
from app.context.project.domain.value_objects.card_appearance import CardAppearance


@dataclass(frozen=True)
class ProjectViewConfig(ValueObject):
    """
    Конфигурация представления проекта.

    Атрибуты:
        view_type: Тип представления.
        filters: Список фильтров.
        sorting: Список правил сортировки.
        grouping: Поле группировки (None — без группировки).
        card_appearance: Настройки карточки.
        column_settings: Настройки колонок.
    """

    view_type: ViewType = ViewType.BOARD
    filters: list[ViewFilter] = field(default_factory=list)
    sorting: list[SortRule] = field(default_factory=list)
    grouping: str | None = None
    card_appearance: CardAppearance | None = None
    column_settings: dict[str, str] | None = None
