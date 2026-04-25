from __future__ import annotations

from fastapi import Depends, Query

from app.shared.presentation.base_controller import BaseController
from app.shared.presentation.responses import (
    ErrorResponse,
    PaginatedResponse,
    SuccessResponse,
)

from app.context.task.application.queries.get_subtasks import (
    GetSubtasksHandler,
    GetSubtasksQuery,
)
from app.context.task.application.queries.get_task_changelog import (
    GetTaskChangelogHandler,
    GetTaskChangelogQuery,
)
from app.context.task.application.queries.get_task_changelog_by_field import (
    GetTaskChangelogByFieldHandler,
    GetTaskChangelogByFieldQuery,
)
from app.context.task.presentation.dependencies import (
    get_current_user_id,
    get_task_changelog_repository,
    get_task_permission_checker,
    get_task_repository,
)
from app.context.task.presentation.schemas.responses.task_response import TaskResponse
from app.context.task.presentation.schemas.responses.changelog_entry_response import ChangelogEntryResponse


class TaskHistoryController(BaseController):
    """
    Контроллер истории и подзадач.

    Endpoint'ы:
        GET /{task_id}/subtasks                 — Подзадачи
        GET /{task_id}/changelog                — История изменений
        GET /{task_id}/changelog/{field_name}   — История поля
    """

    def __init__(self) -> None:
        super().__init__(prefix="/tasks", tags=["Task / History"])

    def _register_routes(self) -> None:
        self._router.add_api_route(
            "/{task_id}/subtasks",
            self.get_subtasks,
            methods=["GET"],
            response_model=PaginatedResponse[TaskResponse],
            summary="Подзадачи",
            description="Возвращает подзадачи указанной задачи.",
            responses={
                200: {"description": "Список подзадач"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Задача не найдена", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{task_id}/changelog",
            self.get_changelog,
            methods=["GET"],
            response_model=PaginatedResponse[ChangelogEntryResponse],
            summary="История изменений задачи",
            description="Возвращает историю изменений задачи.",
            responses={
                200: {"description": "Список записей изменений"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Задача не найдена", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{task_id}/changelog/{field_name}",
            self.get_changelog_by_field,
            methods=["GET"],
            response_model=PaginatedResponse[ChangelogEntryResponse],
            summary="История изменений поля задачи",
            description="Возвращает историю изменений конкретного поля задачи.",
            responses={
                200: {"description": "Список записей изменений поля"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Задача не найдена", "model": ErrorResponse},
            },
        )

    async def get_subtasks(
        self,
        task_id: str,
        offset: int = Query(default=0, ge=0, description="Смещение пагинации"),
        limit: int = Query(default=100, ge=1, le=500, description="Размер страницы"),
        caller_id: str = Depends(get_current_user_id),
        task_repo=Depends(get_task_repository),
        permission_checker=Depends(get_task_permission_checker),
    ) -> PaginatedResponse[TaskResponse]:
        """Подзадачи."""
        handler = GetSubtasksHandler(
            task_repo=task_repo,
            permission_checker=permission_checker,
        )
        query = GetSubtasksQuery(
            caller_id=caller_id,
            parent_task_id=task_id,
        )
        dto = await handler.handle(query)
        items = [TaskResponse.model_validate(item.model_dump()) for item in dto.items]
        page = (offset // max(limit, 1)) + 1
        return PaginatedResponse(items=items, total=dto.total, page=page, page_size=limit)

    async def get_changelog(
        self,
        task_id: str,
        offset: int = Query(default=0, ge=0, description="Смещение пагинации"),
        limit: int = Query(default=100, ge=1, le=500, description="Размер страницы"),
        caller_id: str = Depends(get_current_user_id),
        changelog_repo=Depends(get_task_changelog_repository),
        task_repo=Depends(get_task_repository),
        permission_checker=Depends(get_task_permission_checker),
    ) -> PaginatedResponse[ChangelogEntryResponse]:
        """История изменений задачи."""
        handler = GetTaskChangelogHandler(
            changelog_repo=changelog_repo,
            task_repo=task_repo,
            permission_checker=permission_checker,
        )
        query = GetTaskChangelogQuery(
            caller_id=caller_id,
            task_id=task_id,
            offset=offset,
            limit=limit,
        )
        dto = await handler.handle(query)
        items = [ChangelogEntryResponse.model_validate(item.model_dump()) for item in dto.items]
        page = (offset // max(limit, 1)) + 1
        return PaginatedResponse(items=items, total=dto.total, page=page, page_size=limit)

    async def get_changelog_by_field(
        self,
        task_id: str,
        field_name: str,
        offset: int = Query(default=0, ge=0, description="Смещение пагинации"),
        limit: int = Query(default=100, ge=1, le=500, description="Размер страницы"),
        caller_id: str = Depends(get_current_user_id),
        changelog_repo=Depends(get_task_changelog_repository),
        task_repo=Depends(get_task_repository),
        permission_checker=Depends(get_task_permission_checker),
    ) -> PaginatedResponse[ChangelogEntryResponse]:
        """История изменений конкретного поля задачи."""
        handler = GetTaskChangelogByFieldHandler(
            changelog_repo=changelog_repo,
            task_repo=task_repo,
            permission_checker=permission_checker,
        )
        query = GetTaskChangelogByFieldQuery(
            caller_id=caller_id,
            task_id=task_id,
            field_name=field_name,
            offset=offset,
            limit=limit,
        )
        dto = await handler.handle(query)
        items = [ChangelogEntryResponse.model_validate(item.model_dump()) for item in dto.items]
        page = (offset // max(limit, 1)) + 1
        return PaginatedResponse(items=items, total=dto.total, page=page, page_size=limit)
