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

from app.context.task.application.commands.create_task import (
    CreateTaskCommand,
    CreateTaskHandler,
)
from app.context.task.application.commands.create_task_from_template import (
    CreateTaskFromTemplateCommand,
    CreateTaskFromTemplateHandler,
)
from app.context.task.application.commands.bulk_update_tasks import (
    BulkUpdateTasksCommand,
    BulkUpdateTasksHandler,
)
from app.context.task.application.queries.search_tasks import (
    SearchTasksHandler,
    SearchTasksQuery,
)
from app.context.task.application.queries.count_tasks_by_project import (
    CountTasksByProjectHandler,
    CountTasksByProjectQuery,
)
from app.context.task.application.queries.count_tasks_by_status import (
    CountTasksByStatusHandler,
    CountTasksByStatusQuery,
)
from app.context.task.presentation.dependencies import (
    get_current_user_id,
    get_task_board_port,
    get_task_changelog_repository,
    get_task_epic_port,
    get_task_event_bus,
    get_task_permission_checker,
    get_task_project_port,
    get_task_repository,
    get_task_sprint_port,
    get_task_template_repository,
)
from app.context.task.presentation.schemas.requests.create_task_request import CreateTaskRequest
from app.context.task.presentation.schemas.requests.create_task_from_template_request import CreateTaskFromTemplateRequest
from app.context.task.presentation.schemas.requests.bulk_update_tasks_request import BulkUpdateTasksRequest
from app.context.task.application.queries.get_critical_path import (
    GetCriticalPathHandler,
    GetCriticalPathQuery,
)
from app.context.task.presentation.schemas.responses.task_response import TaskResponse
from app.context.task.presentation.schemas.responses.task_count_response import TaskCountResponse
from app.context.task.presentation.schemas.responses.critical_path_response import CriticalPathResponse


class TaskController(BaseController):
    """
    Контроллер задач проекта.

    Endpoint'ы:
        POST   /{project_id}/tasks                        — Создать задачу
        POST   /{project_id}/tasks/from-template          — Создать из шаблона
        GET    /{project_id}/tasks                        — Поиск задач проекта
        GET    /{project_id}/tasks/count                  — Счётчик задач
        GET    /{project_id}/tasks/count-by-status/{status_id} — Счётчик по статусу
        POST   /{project_id}/tasks/bulk                   — Массовое обновление
        GET    /{project_id}/tasks/critical-path           — Критический путь
    """

    def __init__(self) -> None:
        super().__init__(prefix="/workspaces/{ws_id}/projects", tags=["Task"])

    def _register_routes(self) -> None:
        self._router.add_api_route(
            "/{project_id}/tasks",
            self.create_task,
            methods=["POST"],
            response_model=SuccessResponse[TaskResponse],
            status_code=201,
            summary="Создать задачу",
            description="Создаёт новую задачу в проекте.",
            responses={
                201: {"description": "Задача создана"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                422: {"description": "Ошибка валидации", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{project_id}/tasks/from-template",
            self.create_task_from_template,
            methods=["POST"],
            response_model=SuccessResponse[TaskResponse],
            status_code=201,
            summary="Создать задачу из шаблона",
            description="Создаёт задачу на основе шаблона.",
            responses={
                201: {"description": "Задача создана"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Шаблон не найден", "model": ErrorResponse},
                422: {"description": "Ошибка валидации", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{project_id}/tasks",
            self.search_tasks,
            methods=["GET"],
            response_model=PaginatedResponse[TaskResponse],
            summary="Поиск задач проекта",
            description="Пагинированный поиск задач проекта с фильтрацией.",
            responses={
                200: {"description": "Список задач"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{project_id}/tasks/count",
            self.count_tasks,
            methods=["GET"],
            response_model=SuccessResponse[TaskCountResponse],
            summary="Счётчик задач проекта",
            description="Возвращает количество задач в проекте.",
            responses={
                200: {"description": "Количество задач"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{project_id}/tasks/count-by-status/{status_id}",
            self.count_tasks_by_status,
            methods=["GET"],
            response_model=SuccessResponse[TaskCountResponse],
            summary="Счётчик задач по статусу",
            description="Возвращает количество задач в проекте с указанным статусом.",
            responses={
                200: {"description": "Количество задач"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{project_id}/tasks/bulk",
            self.bulk_update_tasks,
            methods=["POST"],
            response_model=MessageResponse,
            summary="Массовое обновление задач",
            description="Обновляет несколько задач одновременно.",
            responses={
                200: {"description": "Задачи обновлены"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                409: {"description": "Нарушение бизнес-правила", "model": ErrorResponse},
                422: {"description": "Ошибка валидации", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{project_id}/tasks/critical-path",
            self.get_critical_path,
            methods=["GET"],
            response_model=SuccessResponse[CriticalPathResponse],
            summary="Критический путь проекта",
            description="Рассчитывает критический путь проекта на основе зависимостей (BLOCKS) и дат задач.",
            responses={
                200: {"description": "Критический путь"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
            },
        )

    async def create_task(
        self,
        ws_id: str,
        project_id: str,
        body: CreateTaskRequest,
        caller_id: str = Depends(get_current_user_id),
        task_repo=Depends(get_task_repository),
        permission_checker=Depends(get_task_permission_checker),
        project_port=Depends(get_task_project_port),
        board_port=Depends(get_task_board_port),
        event_bus=Depends(get_task_event_bus),
    ) -> SuccessResponse[TaskResponse]:
        """Создать задачу в проекте."""
        handler = CreateTaskHandler(
            task_repo=task_repo,
            permission_checker=permission_checker,
            project_port=project_port,
            board_port=board_port,
            event_bus=event_bus,
        )
        command = CreateTaskCommand(
            caller_id=caller_id,
            project_id=project_id,
            title=body.title,
            task_type=body.task_type,
            reporter_id=body.reporter_id or caller_id,
            parent_task_id=body.parent_task_id,
            epic_id=body.epic_id,
        )
        dto = await handler.handle(command)
        return SuccessResponse(data=TaskResponse.model_validate(dto.model_dump()))

    async def create_task_from_template(
        self,
        ws_id: str,
        project_id: str,
        body: CreateTaskFromTemplateRequest,
        caller_id: str = Depends(get_current_user_id),
        task_repo=Depends(get_task_repository),
        template_repo=Depends(get_task_template_repository),
        permission_checker=Depends(get_task_permission_checker),
        project_port=Depends(get_task_project_port),
        board_port=Depends(get_task_board_port),
        event_bus=Depends(get_task_event_bus),
    ) -> SuccessResponse[TaskResponse]:
        """Создать задачу из шаблона."""
        handler = CreateTaskFromTemplateHandler(
            task_repo=task_repo,
            template_repo=template_repo,
            project_port=project_port,
            board_port=board_port,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        command = CreateTaskFromTemplateCommand(
            caller_id=caller_id,
            project_id=project_id,
            template_id=body.template_id,
            reporter_id=body.reporter_id,
        )
        dto = await handler.handle(command)
        return SuccessResponse(data=TaskResponse.model_validate(dto.model_dump()))

    async def search_tasks(
        self,
        ws_id: str,
        project_id: str,
        offset: int = Query(default=0, ge=0, description="Смещение пагинации"),
        limit: int = Query(default=100, ge=1, le=500, description="Размер страницы"),
        status: str | None = Query(default=None, description="Фильтр по статусу"),
        priority: str | None = Query(default=None, description="Фильтр по приоритету"),
        task_type: str | None = Query(default=None, description="Фильтр по типу"),
        label: str | None = Query(default=None, description="Фильтр по метке"),
        assignee: str | None = Query(default=None, description="Фильтр по исполнителю"),
        search: str | None = Query(default=None, description="Текстовый поиск"),
        start_date_from: str | None = Query(default=None, description="Дата начала от (ISO)"),
        start_date_to: str | None = Query(default=None, description="Дата начала до (ISO)"),
        due_date_from: str | None = Query(default=None, description="Дедлайн от (ISO)"),
        due_date_to: str | None = Query(default=None, description="Дедлайн до (ISO)"),
        sort_by: str | None = Query(default=None, description="Поле сортировки (start_date, due_date, created_at, updated_at, priority, title)"),
        sort_order: str = Query(default="asc", description="Порядок сортировки (asc/desc)"),
        caller_id: str = Depends(get_current_user_id),
        task_repo=Depends(get_task_repository),
        permission_checker=Depends(get_task_permission_checker),
    ) -> PaginatedResponse[TaskResponse]:
        """Поиск задач проекта."""
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
        if search:
            filters["search"] = search
        if start_date_from:
            filters["start_date_from"] = start_date_from
        if start_date_to:
            filters["start_date_to"] = start_date_to
        if due_date_from:
            filters["due_date_from"] = due_date_from
        if due_date_to:
            filters["due_date_to"] = due_date_to

        handler = SearchTasksHandler(
            task_repo=task_repo,
            permission_checker=permission_checker,
        )
        query = SearchTasksQuery(
            caller_id=caller_id,
            project_id=project_id,
            offset=offset,
            limit=limit,
            filters=filters or None,
            sort_by=sort_by,
            sort_order=sort_order,
        )
        dto = await handler.handle(query)
        items = [TaskResponse.model_validate(item.model_dump()) for item in dto.items]
        page = (offset // max(limit, 1)) + 1
        return PaginatedResponse(items=items, total=dto.total, page=page, page_size=limit)

    async def count_tasks(
        self,
        ws_id: str,
        project_id: str,
        caller_id: str = Depends(get_current_user_id),
        task_repo=Depends(get_task_repository),
        permission_checker=Depends(get_task_permission_checker),
    ) -> SuccessResponse[TaskCountResponse]:
        """Счётчик задач проекта."""
        handler = CountTasksByProjectHandler(
            task_repo=task_repo,
            permission_checker=permission_checker,
        )
        query = CountTasksByProjectQuery(caller_id=caller_id, project_id=project_id)
        dto = await handler.handle(query)
        return SuccessResponse(data=TaskCountResponse(count=dto.count))

    async def count_tasks_by_status(
        self,
        ws_id: str,
        project_id: str,
        status_id: str,
        caller_id: str = Depends(get_current_user_id),
        task_repo=Depends(get_task_repository),
        permission_checker=Depends(get_task_permission_checker),
    ) -> SuccessResponse[TaskCountResponse]:
        """Счётчик задач по статусу."""
        handler = CountTasksByStatusHandler(
            task_repo=task_repo,
            permission_checker=permission_checker,
        )
        query = CountTasksByStatusQuery(
            caller_id=caller_id,
            project_id=project_id,
            status_id=status_id,
        )
        dto = await handler.handle(query)
        return SuccessResponse(data=TaskCountResponse(count=dto.count))

    async def bulk_update_tasks(
        self,
        ws_id: str,
        project_id: str,
        body: BulkUpdateTasksRequest,
        caller_id: str = Depends(get_current_user_id),
        task_repo=Depends(get_task_repository),
        changelog_repo=Depends(get_task_changelog_repository),
        permission_checker=Depends(get_task_permission_checker),
        board_port=Depends(get_task_board_port),
        sprint_port=Depends(get_task_sprint_port),
        epic_port=Depends(get_task_epic_port),
        event_bus=Depends(get_task_event_bus),
    ) -> MessageResponse:
        """Массовое обновление задач."""
        handler = BulkUpdateTasksHandler(
            task_repo=task_repo,
            changelog_repo=changelog_repo,
            board_port=board_port,
            sprint_port=sprint_port,
            epic_port=epic_port,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        command = BulkUpdateTasksCommand(
            task_ids=body.task_ids,
            changes=body.changes,
            changed_by=caller_id,
        )
        await handler.handle(command)
        return SuccessResponse(data=MessageData(message="Задачи обновлены"))

    async def get_critical_path(
        self,
        ws_id: str,
        project_id: str,
        caller_id: str = Depends(get_current_user_id),
        task_repo=Depends(get_task_repository),
        permission_checker=Depends(get_task_permission_checker),
    ) -> SuccessResponse[CriticalPathResponse]:
        """Критический путь проекта."""
        handler = GetCriticalPathHandler(
            task_repo=task_repo,
            permission_checker=permission_checker,
        )
        query = GetCriticalPathQuery(
            caller_id=caller_id,
            project_id=project_id,
        )
        dto = await handler.handle(query)
        return SuccessResponse(data=CriticalPathResponse.model_validate(dto.model_dump()))
