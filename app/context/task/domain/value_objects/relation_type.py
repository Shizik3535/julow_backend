from __future__ import annotations

from enum import Enum


class RelationType(Enum):
    """
    Тип связи между задачами.

    Новые типы связей = значение enum.

    Значения:
        BLOCKS: Блокирует
        IS_BLOCKED_BY: Блокируется
        RELATES_TO: Связана с
        DUPLICATES: Дублирует
        IS_DUPLICATED_BY: Дублируется
        CAUSES: Вызывает
        IS_CAUSED_BY: Вызвана
        PARENT: Родительская
        CHILD: Дочерняя
        FOLLOWS: Следует за
        PRECEDES: Предшествует
    """

    BLOCKS = "blocks"
    IS_BLOCKED_BY = "is_blocked_by"
    RELATES_TO = "relates_to"
    DUPLICATES = "duplicates"
    IS_DUPLICATED_BY = "is_duplicated_by"
    CAUSES = "causes"
    IS_CAUSED_BY = "is_caused_by"
    PARENT = "parent"
    CHILD = "child"
    FOLLOWS = "follows"
    PRECEDES = "precedes"
