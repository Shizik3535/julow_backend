from __future__ import annotations

from fastapi import Depends, Query

from app.shared.presentation.base_controller import BaseController
from app.shared.presentation.responses import (
    ErrorResponse,
    PaginatedResponse,
    SuccessResponse,
)

from app.context.project.application.queries.get_projects_by_member import (
    GetProjectsByMemberHandler,
    GetProjectsByMemberQuery,
)
from app.context.project.application.queries.get_overdue_projects import (
    GetOverdueProjectsHandler,
    GetOverdueProjectsQuery,
)
from app.context.project.application.queries.search_projects import (
    SearchProjectsHandler,
    SearchProjectsQuery,
)
from app.context.project.presentation.dependencies import (
    get_current_user_id,
    get_project_permission_checker,
    get_project_repository,
)
from app.context.project.presentation.schemas.responses.project_response import (
    ProjectResponse,
)


class MyProjectsController(BaseController):
    """
    Контроллер «Мои проекты» и глобального поиска.

    Endpoint'ы:
        GET /projects/mine          — Проекты текущего пользователя
        GET /projects/mine/overdue  — Мои просроченные проекты
        GET /projects/              — Глобальный поиск проектов
    """

    def __init__(self) -> None:
        super().__init__(prefix="/projects", tags=["Project / My Projects"])

    def _register_routes(self) -> None:
        self._router.add_api_route(
            "/mine",
            self.get_my_projects,
            methods=["GET"],
            response_model=SuccessResponse[list[ProjectResponse]],
            summary="Мои проекты",
            description="Возвращает все проекты, где текущий пользователь является участником.",
            responses={401: {"description": "Не аутентифицирован", "model": ErrorResponse}},
        )
        self._router.add_api_route(
            "/mine/overdue",
            self.get_my_overdue_projects,
            methods=["GET"],
            response_model=SuccessResponse[list[ProjectResponse]],
            summary="Мои просроченные проекты",
            description="Просроченные проекты, в которых текущий пользователь — участник или владелец.",
            responses={
                200: {"description": "Список просроченных проектов"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/",
            self.search_projects,
            methods=["GET"],
            response_model=PaginatedResponse[ProjectResponse],
            summary="Поиск проектов",
            description="Глобальный поиск проектов с фильтрацией по тексту, workspace, методологии.",
            responses={200: {"description": "Результаты поиска"}},
        )

    async def get_my_projects(
        self,
        caller_id: str = Depends(get_current_user_id),
        project_repo=Depends(get_project_repository),
        permission_checker=Depends(get_project_permission_checker),
    ) -> SuccessResponse[list[ProjectResponse]]:
        handler = GetProjectsByMemberHandler(project_repo=project_repo, permission_checker=permission_checker)
        query = GetProjectsByMemberQuery(caller_id=caller_id, user_id=caller_id)
        dto = await handler.handle(query)
        items = [ProjectResponse.model_validate(item.__dict__) for item in dto.items]
        return SuccessResponse(data=items)

    async def get_my_overdue_projects(
        self,
        caller_id: str = Depends(get_current_user_id),
        project_repo=Depends(get_project_repository),
        permission_checker=Depends(get_project_permission_checker),
    ) -> SuccessResponse[list[ProjectResponse]]:
        handler = GetOverdueProjectsHandler(project_repo=project_repo, permission_checker=permission_checker)
        query = GetOverdueProjectsQuery(caller_id=caller_id)
        dto = await handler.handle(query)
        items = [ProjectResponse.model_validate(item.__dict__) for item in dto.items]
        return SuccessResponse(data=items)

    async def search_projects(
        self,
        query: str = Query("", description="Поисковый запрос"),
        workspace_id: str | None = Query(None, description="UUID workspace для фильтрации"),
        offset: int = Query(0, ge=0, description="Смещение"),
        limit: int = Query(100, ge=1, le=500, description="Лимит"),
        caller_id: str = Depends(get_current_user_id),
        project_repo=Depends(get_project_repository),
        permission_checker=Depends(get_project_permission_checker),
    ) -> PaginatedResponse[ProjectResponse]:
        handler = SearchProjectsHandler(project_repo=project_repo, permission_checker=permission_checker)
        search_query = SearchProjectsQuery(
            caller_id=caller_id,
            search_text=query if query else None,
            workspace_id=workspace_id,
            offset=offset,
            limit=limit,
        )
        dto = await handler.handle(search_query)
        items = [ProjectResponse.model_validate(item.__dict__) for item in dto.items]
        page = (offset // limit) + 1 if limit > 0 else 1
        return PaginatedResponse(items=items, total=dto.total, page=page, page_size=limit)
