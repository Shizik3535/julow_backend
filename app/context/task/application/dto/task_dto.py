from __future__ import annotations

from datetime import datetime
from typing import Any

from app.shared.application.base_dto import BaseDTO


class TaskDTO(BaseDTO):
    """
    DTO задачи (Task BC).

    Атрибуты:
        id: Идентификатор задачи.
        project_id: ID проекта.
        parent_task_id: ID родительской задачи.
        epic_id: ID эпика.
        title: Заголовок.
        description: Описание (dict).
        status_id: ID workflow-статуса.
        priority: Приоритет.
        task_type: Тип задачи.
        assignee_ids: ID исполнителей.
        reporter_id: ID автора.
        labels: Метки.
        progress: Прогресс (0–100).
        effort_estimate: Оценка усилия.
        actual_effort: Фактическое усилие.
        start_date: Дата начала.
        due_date: Дедлайн.
        completed_at: Время завершения.
        custom_fields: Кастомные поля.
        checklists: Чек-листы.
        relations: Связи.
        watchers: Наблюдатели.
        attachments: Вложения.
        order: Позиция на доске.
        sprint_id: ID спринта.
        status: Жизненный цикл задачи.
        recurrence: Конфигурация повторения.
        created_at: Время создания.
        updated_at: Время обновления.
    """

    id: str
    project_id: str
    parent_task_id: str | None = None
    epic_id: str | None = None
    title: str = ""
    description: dict[str, Any] | None = None
    status_id: str | None = None
    priority: str = "NONE"
    task_type: str = "TASK"
    assignee_ids: list[str] = []
    reporter_id: str | None = None
    labels: list[dict[str, Any]] = []
    progress: int = 0
    effort_estimate: dict[str, Any] | None = None
    actual_effort: dict[str, Any] | None = None
    start_date: str | None = None
    due_date: str | None = None
    completed_at: datetime | None = None
    custom_fields: dict[str, str] = {}
    checklists: list[dict[str, Any]] = []
    relations: list[dict[str, Any]] = []
    watchers: list[dict[str, Any]] = []
    attachments: list[dict[str, Any]] = []
    order: dict[str, Any] | None = None
    sprint_id: str | None = None
    status: str = "ACTIVE"
    recurrence: dict[str, Any] | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class TaskListDTO(BaseDTO):
    """Список задач с total."""

    items: list[TaskDTO]
    total: int
