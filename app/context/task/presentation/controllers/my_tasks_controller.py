from __future__ import annotations

from typing import Any

from fastapi import Depends, Query

from app.shared.presentation.base_controller import BaseController
from app.shared.presentation.responses import (
    ErrorResponse,
    MessageData,
    MessageResponse,
    PaginatedResponse,
    SuccessResponse,
)

from app.context.task.application.queries.search_tasks import (
    SearchTasksHandler,
    SearchTasksQuery,
)
from app.context.task.application.queries.get_overdue_tasks import (
    GetOverdueTasksHandler,
    GetOverdueTasksQuery,
)
from app.context.task.presentation.dependencies import (
    get_current_user_id,
    get_task_permission_checker,
    get_task_repository,
)
from app.context.task.presentation.schemas.responses.task_response import TaskResponse


class MyTasksController(BaseController):
    """
    Контроллер моих задач.

    Endpoint'ы:
        GET    /mine            — Мои задачи (поиск с фильтрацией)
        GET    /mine/overdue    — Мои просроченные задачи
    """

    def __init__(self) -> None:
        super().__init__(prefix="/tasks", tags=["Task / My Tasks"])

    def _register_routes(self) -> None:
        self._router.add_api_route(
            "/mine",
            self.search_my_tasks,
            methods=["GET"],
            response_model=PaginatedResponse[TaskResponse],
            summary="Мои задачи",
            description="Поиск задач, в которых текущий пользователь — исполнитель, автор или наблюдатель.",
            responses={
                200: {"description": "Список задач"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/mine/overdue",
            self.get_my_overdue_tasks,
            methods=["GET"],
            response_model=PaginatedResponse[TaskResponse],
            summary="Мои просроченные задачи",
            description="Просроченные задачи, в которых текущий пользователь участвует.",
            responses={
                200: {"description": "Список просроченных задач"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
            },
        )

    async def search_my_tasks(
        self,
        offset: int = Query(default=0, ge=0, description="Смещение пагинации"),
        limit: int = Query(default=100, ge=1, le=500, description="Размер страницы"),
        status: str | None = Query(default=None, description="Фильтр по статусу"),
        priority: str | None = Query(default=None, description="Фильтр по приоритету"),
        task_type: str | None = Query(default=None, description="Фильтр по типу задачи"),
        label: str | None = Query(default=None, description="Фильтр по метке"),
        assignee: str | None = Query(default=None, description="Фильтр по исполнителю"),
        role: str | None = Query(default=None, description="Роль участия (assignee / reporter / watcher / all)"),
        due_before: str | None = Query(default=None, description="Дедлайн до (ISO date)"),
        due_after: str | None = Query(default=None, description="Дедлайн после (ISO date)"),
        search: str | None = Query(default=None, description="Текстовый поиск"),
        caller_id: str = Depends(get_current_user_id),
        task_repo=Depends(get_task_repository),
        permission_checker=Depends(get_task_permission_checker),
    ) -> PaginatedResponse[TaskResponse]:
        """Мои задачи (кросс-проектный поиск)."""
        filters: dict[str, Any] = {}
        if status:
            filters["status"] = status
        if priority:
            filters["priority"] = priority
        if task_type:
            filters["task_type"] = task_type
        if label:
            filters["label"] = label
        if assignee:
            filters["assignee"] = assignee
        if role:
            filters["role"] = role
        if due_before:
            filters["due_before"] = due_before
        if due_after:
            filters["due_after"] = due_after
        if search:
            filters["search"] = search

        handler = SearchTasksHandler(
            task_repo=task_repo,
            permission_checker=permission_checker,
        )
        query = SearchTasksQuery(
            caller_id=caller_id,
            project_id=None,
            offset=offset,
            limit=limit,
            filters=filters or None,
        )
        dto = await handler.handle(query)
        items = [TaskResponse.model_validate(item.model_dump()) for item in dto.items]
        page = (offset // max(limit, 1)) + 1
        return PaginatedResponse(items=items, total=dto.total, page=page, page_size=limit)

    async def get_my_overdue_tasks(
        self,
        caller_id: str = Depends(get_current_user_id),
        task_repo=Depends(get_task_repository),
        permission_checker=Depends(get_task_permission_checker),
    ) -> PaginatedResponse[TaskResponse]:
        """Мои просроченные задачи."""
        handler = GetOverdueTasksHandler(
            task_repo=task_repo,
            permission_checker=permission_checker,
        )
        query = GetOverdueTasksQuery(caller_id=caller_id, project_id=None)
        dto = await handler.handle(query)
        items = [TaskResponse.model_validate(item.model_dump()) for item in dto.items]
        return PaginatedResponse(items=items, total=dto.total, page=1, page_size=dto.total)
