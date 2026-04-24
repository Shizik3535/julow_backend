from __future__ import annotations

from enum import Enum


class Methodology(Enum):
    """
    Методология управления проектом.

    Значения:
        KANBAN: Канбан-методология
        SCRUM: Скрам-методология
        WATERFALL: Каскадная методология
        HYBRID: Гибридная методология
        SHAPE_UP: Shape Up методология
    """

    KANBAN = "kanban"
    SCRUM = "scrum"
    WATERFALL = "waterfall"
    HYBRID = "hybrid"
    SHAPE_UP = "shape_up"
