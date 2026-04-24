from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class BaseQuery(BaseModel):
    """
    Базовый запрос (Query).

    Query — это запрос на чтение данных из домена.
    Именуется в вопросительной форме или как существительное:
    GetTaskById, ListTasks, FindUsers.

    Query:
        - Не изменяет состояние (только чтение)
        - Возвращает DTO / проекцию
        - Может использовать отдельную модель чтения (CQRS)
        - Валидируется перед выполнением (Pydantic)
        - Неизменяема (frozen)

    Пример:
        class GetTaskByIdQuery(BaseQuery):
            task_id: Id

        class ListTasksQuery(BaseQuery):
            status: str | None = None
            page: int = 1
            page_size: int = 20
    """

    model_config = ConfigDict(
        frozen=True,
        populate_by_name=True,
        from_attributes=True,
    )
