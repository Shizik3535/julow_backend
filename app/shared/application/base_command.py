from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class BaseCommand(BaseModel):
    """
    Базовая команда (Command).

    Команда — это запрос на изменение состояния домена.
    Именуется в повелительном наклонении: CreateTask, AssignUser, DeleteProject.

    Команда:
        - Не возвращает результат (или возвращает минимальный — ID)
        - Может порождать доменные события
        - Валидируется перед выполнением (Pydantic)
        - Неизменяема (frozen)

    Пример:
        class CreateTaskCommand(BaseCommand):
            title: str
            description: str | None = None
            assignee_id: Id
    """

    model_config = ConfigDict(
        frozen=True,
        populate_by_name=True,
        from_attributes=True,
    )
