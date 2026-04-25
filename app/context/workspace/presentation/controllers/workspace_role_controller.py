from __future__ import annotations

from fastapi import Depends, Query

from app.shared.presentation.base_controller import BaseController
from app.shared.presentation.responses import (
    ErrorResponse,
    MessageResponse,
    PaginatedResponse,
    SuccessResponse,
)

from app.context.workspace.application.commands.create_workspace_role import (
    CreateWorkspaceRoleCommand,
    CreateWorkspaceRoleHandler,
)
from app.context.workspace.application.commands.update_workspace_role import (
    UpdateWorkspaceRoleCommand,
    UpdateWorkspaceRoleHandler,
)
from app.context.workspace.application.commands.delete_workspace_role import (
    DeleteWorkspaceRoleCommand,
    DeleteWorkspaceRoleHandler,
)
from app.context.workspace.application.queries.get_workspace_roles import (
    GetWorkspaceRolesHandler,
    GetWorkspaceRolesQuery,
)
from app.context.workspace.application.queries.get_workspace_role import (
    GetWorkspaceRoleHandler,
    GetWorkspaceRoleQuery,
)
from app.context.workspace.presentation.dependencies import (
    get_current_user_id,
    get_workspace_event_bus,
    get_workspace_permission_checker,
    get_workspace_repository,
    get_workspace_role_repository,
)
from app.context.workspace.presentation.schemas.requests.create_workspace_role_request import CreateWorkspaceRoleRequest
from app.context.workspace.presentation.schemas.requests.update_workspace_role_request import UpdateWorkspaceRoleRequest
from app.context.workspace.presentation.schemas.responses.workspace_role_response import WorkspaceRoleResponse


class WorkspaceRoleController(BaseController):
    """
    Контроллер ролей workspace.

    Endpoint'ы:
        GET    /{ws_id}/roles                     — Список ролей
        GET    /{ws_id}/roles/{role_id}            — Получить роль
        POST   /{ws_id}/roles                     — Создать кастомную роль
        PATCH  /{ws_id}/roles/{role_id}            — Обновить роль
        DELETE /{ws_id}/roles/{role_id}            — Удалить кастомную роль
    """

    def __init__(self) -> None:
        super().__init__(prefix="/workspaces", tags=["Workspace / Roles"])

    def _register_routes(self) -> None:
        self._router.add_api_route(
            "/{ws_id}/roles",
            self.get_roles,
            methods=["GET"],
            response_model=PaginatedResponse[WorkspaceRoleResponse],
            summary="Список ролей workspace",
            description="Возвращает список ролей workspace. Параметр system_only — только системные роли.",
            responses={
                200: {"description": "Список ролей"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Workspace не найден", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{ws_id}/roles/{role_id}",
            self.get_role,
            methods=["GET"],
            response_model=SuccessResponse[WorkspaceRoleResponse],
            summary="Получить роль workspace",
            description="Возвращает данные роли workspace по UUID.",
            responses={
                200: {"description": "Данные роли"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Роль не найдена", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{ws_id}/roles",
            self.create_role,
            methods=["POST"],
            response_model=SuccessResponse[WorkspaceRoleResponse],
            status_code=201,
            summary="Создать кастомную роль",
            description="Создаёт кастомную роль в workspace с указанными разрешениями.",
            responses={
                201: {"description": "Роль создана"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Workspace не найден", "model": ErrorResponse},
                409: {"description": "Роль с таким именем уже существует", "model": ErrorResponse},
                422: {"description": "Ошибка валидации", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{ws_id}/roles/{role_id}",
            self.update_role,
            methods=["PATCH"],
            response_model=MessageResponse,
            summary="Обновить роль workspace",
            description="Обновляет разрешения или описание кастомной роли.",
            responses={
                200: {"description": "Роль обновлена"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Роль не найдена", "model": ErrorResponse},
                422: {"description": "Ошибка валидации", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{ws_id}/roles/{role_id}",
            self.delete_role,
            methods=["DELETE"],
            response_model=MessageResponse,
            summary="Удалить кастомную роль",
            description="Удаляет кастомную роль workspace. Системные роли удалить нельзя.",
            responses={
                200: {"description": "Роль удалена"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав или системная роль", "model": ErrorResponse},
                404: {"description": "Роль не найдена", "model": ErrorResponse},
                409: {"description": "Роль используется участниками", "model": ErrorResponse},
            },
        )

    # ------------------------------------------------------------------
    # Workspace Roles
    # ------------------------------------------------------------------

    async def get_roles(
        self,
        ws_id: str,
        system_only: bool = Query(default=False, description="Только системные роли"),
        offset: int = Query(default=0, ge=0, description="Смещение пагинации"),
        limit: int = Query(default=100, ge=1, le=500, description="Размер страницы"),
        caller_id: str = Depends(get_current_user_id),
        role_repo=Depends(get_workspace_role_repository),
        ws_repo=Depends(get_workspace_repository),
        permission_checker=Depends(get_workspace_permission_checker),
    ) -> PaginatedResponse[WorkspaceRoleResponse]:
        """Список ролей workspace."""
        handler = GetWorkspaceRolesHandler(
            role_repo=role_repo,
            ws_repo=ws_repo,
            permission_checker=permission_checker,
        )
        query = GetWorkspaceRolesQuery(
            caller_id=caller_id,
            workspace_id=ws_id,
            system_only=system_only,
        )
        dto = await handler.handle(query)
        items = [WorkspaceRoleResponse.model_validate(item.model_dump()) for item in dto.items]
        page = (offset // max(limit, 1)) + 1
        return PaginatedResponse(items=items, total=dto.total, page=page, page_size=limit)

    async def get_role(
        self,
        ws_id: str,
        role_id: str,
        caller_id: str = Depends(get_current_user_id),
        role_repo=Depends(get_workspace_role_repository),
        permission_checker=Depends(get_workspace_permission_checker),
    ) -> SuccessResponse[WorkspaceRoleResponse]:
        """Получить роль workspace."""
        handler = GetWorkspaceRoleHandler(
            role_repo=role_repo,
            permission_checker=permission_checker,
        )
        query = GetWorkspaceRoleQuery(caller_id=caller_id, role_id=role_id)
        dto = await handler.handle(query)
        return SuccessResponse(data=WorkspaceRoleResponse.model_validate(dto.model_dump()))

    async def create_role(
        self,
        ws_id: str,
        body: CreateWorkspaceRoleRequest,
        caller_id: str = Depends(get_current_user_id),
        role_repo=Depends(get_workspace_role_repository),
        ws_repo=Depends(get_workspace_repository),
        permission_checker=Depends(get_workspace_permission_checker),
        event_bus=Depends(get_workspace_event_bus),
    ) -> SuccessResponse[WorkspaceRoleResponse]:
        """Создать кастомную роль."""
        handler = CreateWorkspaceRoleHandler(
            role_repo=role_repo,
            ws_repo=ws_repo,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        command = CreateWorkspaceRoleCommand(
            caller_id=caller_id,
            workspace_id=ws_id,
            name=body.name,
            permissions=body.permissions,
            description=body.description,
        )
        dto = await handler.handle(command)
        return SuccessResponse(data=WorkspaceRoleResponse.model_validate(dto.model_dump()))

    async def update_role(
        self,
        ws_id: str,
        role_id: str,
        body: UpdateWorkspaceRoleRequest,
        caller_id: str = Depends(get_current_user_id),
        role_repo=Depends(get_workspace_role_repository),
        permission_checker=Depends(get_workspace_permission_checker),
        event_bus=Depends(get_workspace_event_bus),
    ) -> MessageResponse:
        """Обновить роль workspace."""
        handler = UpdateWorkspaceRoleHandler(
            role_repo=role_repo,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        command = UpdateWorkspaceRoleCommand(
            caller_id=caller_id,
            role_id=role_id,
            permissions=body.permissions,
            description=body.description,
        )
        await handler.handle(command)
        return SuccessResponse(data={"message": "Роль обновлена"})

    async def delete_role(
        self,
        ws_id: str,
        role_id: str,
        caller_id: str = Depends(get_current_user_id),
        role_repo=Depends(get_workspace_role_repository),
        permission_checker=Depends(get_workspace_permission_checker),
        event_bus=Depends(get_workspace_event_bus),
    ) -> MessageResponse:
        """Удалить кастомную роль."""
        handler = DeleteWorkspaceRoleHandler(
            role_repo=role_repo,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        command = DeleteWorkspaceRoleCommand(
            caller_id=caller_id,
            role_id=role_id,
        )
        await handler.handle(command)
        return SuccessResponse(data={"message": "Роль удалена"})
