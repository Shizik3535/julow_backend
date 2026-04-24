from __future__ import annotations

from enum import Enum


class CommentTargetType(Enum):
    """
    Тип комментируемой сущности.

    Новые комментируемые сущности = значение enum.

    Значения:
        TASK: Задача
        PROJECT: Проект
        EPIC: Эпик
        MILESTONE: Milestone
        SPRINT: Спринт
        MEETING: Совещание
        DOCUMENT: Документ
    """

    TASK = "task"
    PROJECT = "project"
    EPIC = "epic"
    MILESTONE = "milestone"
    SPRINT = "sprint"
    MEETING = "meeting"
    DOCUMENT = "document"
