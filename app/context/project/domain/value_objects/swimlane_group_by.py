from __future__ import annotations

from enum import Enum


class SwimlaneGroupBy(Enum):
    """
    Способ группировки swimlane.

    Значения:
        ASSIGNEE: По исполнителю
        PRIORITY: По приоритету
        LABEL: По метке
        EPIC: По эпику
        CUSTOM_FIELD: По кастомному полю
    """

    ASSIGNEE = "assignee"
    PRIORITY = "priority"
    LABEL = "label"
    EPIC = "epic"
    CUSTOM_FIELD = "custom_field"
