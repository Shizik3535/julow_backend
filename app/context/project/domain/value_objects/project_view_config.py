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

    def to_dict(self) -> dict:
        """Сериализует конфиг в dict для хранения в JSON-колонке."""
        return {
            "view_type": self.view_type.value,
            "filters": [
                {"field": f.field, "operator": f.operator.value, "value": f.value}
                for f in self.filters
            ],
            "sorting": [
                {"field": s.field, "direction": s.direction.value}
                for s in self.sorting
            ],
            "grouping": self.grouping,
            "card_appearance": {
                "visible_fields": self.card_appearance.visible_fields,
                "compact_mode": self.card_appearance.compact_mode,
                "show_cover_image": self.card_appearance.show_cover_image,
            } if self.card_appearance else None,
            "column_settings": self.column_settings,
        }

    @classmethod
    def from_dict(cls, data: dict) -> ProjectViewConfig:
        """Десериализует конфиг из dict (JSON-колонка)."""
        from app.context.project.domain.value_objects.filter_operator import FilterOperator
        from app.context.project.domain.value_objects.sort_direction import SortDirection

        filters = [
            ViewFilter(
                field=f["field"],
                operator=FilterOperator(f["operator"]),
                value=f.get("value", ""),
            )
            for f in data.get("filters", [])
        ]
        sorting = [
            SortRule(
                field=s["field"],
                direction=SortDirection(s["direction"]),
            )
            for s in data.get("sorting", [])
        ]
        card_data = data.get("card_appearance")
        card_appearance = CardAppearance(
            visible_fields=card_data.get("visible_fields", []),
            compact_mode=card_data.get("compact_mode", False),
            show_cover_image=card_data.get("show_cover_image", True),
        ) if card_data else None

        return cls(
            view_type=ViewType(data.get("view_type", "board")),
            filters=filters,
            sorting=sorting,
            grouping=data.get("grouping"),
            card_appearance=card_appearance,
            column_settings=data.get("column_settings"),
        )
