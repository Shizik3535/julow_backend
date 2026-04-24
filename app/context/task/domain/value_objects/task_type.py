from __future__ import annotations

from enum import Enum


class TaskType(Enum):
    """
    Тип задачи.

    Новые типы задач = значение enum. Иерархия определяется через
    parent_task_id, не через тип.

    Значения:
        EPIC: Эпик
        STORY: Пользовательская история
        TASK: Задача
        SUBTASK: Подзадача
        BUG: Баг
        FEATURE: Фича
        IMPROVEMENT: Улучшение
        TEST_CASE: Тест-кейс
        SPIKE: Спайк
        DOCUMENTATION: Документация
    """

    EPIC = "epic"
    STORY = "story"
    TASK = "task"
    SUBTASK = "subtask"
    BUG = "bug"
    FEATURE = "feature"
    IMPROVEMENT = "improvement"
    TEST_CASE = "test_case"
    SPIKE = "spike"
    DOCUMENTATION = "documentation"
