from __future__ import annotations

from fastapi import Depends

from app.shared.presentation.base_controller import BaseController
from app.shared.presentation.responses import ErrorResponse, MessageResponse, SuccessResponse

from app.context.project.application.commands.create_project_role import (
    CreateProjectRoleCommand,
    CreateProjectRoleHandler,
)
from app.context.project.application.commands.update_project_role import (
    UpdateProjectRoleCommand,
    UpdateProjectRoleHandler,
)
from app.context.project.application.commands.delete_project_role import (
    DeleteProjectRoleCommand,
    DeleteProjectRoleHandler,
)
from app.context.project.application.queries.get_project_roles import (
    GetProjectRolesHandler,
    GetProjectRolesQuery,
)
from app.context.project.application.queries.get_project_role import (
    GetProjectRoleHandler,
    GetProjectRoleQuery,
)
from app.context.project.presentation.dependencies import (
    get_current_user_id,
    get_project_event_bus,
    get_project_permission_checker,
    get_project_repository,
    get_project_role_repository,
)
from app.context.project.presentation.schemas.requests.create_project_role_request import (
    CreateProjectRoleRequest,
)
from app.context.project.presentation.schemas.requests.update_project_role_request import (
    UpdateProjectRoleRequest,
)
from app.context.project.presentation.schemas.responses.project_role_response import (
    ProjectRoleResponse,
)


class ProjectRoleController(BaseController):
    """
    Контроллер ролей проекта.

    Endpoint'ы:
        GET    /{project_id}/roles             — Список ролей
        GET    /{project_id}/roles/{role_id}    — Получить роль
        POST   /{project_id}/roles             — Создать кастомную роль
        PATCH  /{project_id}/roles/{role_id}    — Обновить роль
        DELETE /{project_id}/roles/{role_id}    — Удалить роль
    """

    def __init__(self) -> None:
        super().__init__(prefix="/workspaces/{ws_id}/projects", tags=["Project / Roles"])

    def _register_routes(self) -> None:
        self._router.add_api_route(
            "/{project_id}/roles", self.list_roles, methods=["GET"],
            response_model=SuccessResponse[list[ProjectRoleResponse]],
            summary="Список ролей проекта",
        )
        self._router.add_api_route(
            "/{project_id}/roles/{role_id}", self.get_role, methods=["GET"],
            response_model=SuccessResponse[ProjectRoleResponse],
            summary="Получить роль проекта",
            responses={404: {"model": ErrorResponse}},
        )
        self._router.add_api_route(
            "/{project_id}/roles", self.create_role, methods=["POST"],
            response_model=SuccessResponse[ProjectRoleResponse], status_code=201,
            summary="Создать кастомную роль",
        )
        self._router.add_api_route(
            "/{project_id}/roles/{role_id}", self.update_role, methods=["PATCH"],
            response_model=MessageResponse, summary="Обновить роль проекта",
        )
        self._router.add_api_route(
            "/{project_id}/roles/{role_id}", self.delete_role, methods=["DELETE"],
            response_model=MessageResponse, summary="Удалить роль проекта",
        )

    async def list_roles(
        self, ws_id: str, project_id: str,
        caller_id: str = Depends(get_current_user_id),
        role_repo=Depends(get_project_role_repository),
        permission_checker=Depends(get_project_permission_checker),
    ) -> SuccessResponse[list[ProjectRoleResponse]]:
        handler = GetProjectRolesHandler(role_repo=role_repo, permission_checker=permission_checker)
        query = GetProjectRolesQuery(caller_id=caller_id, project_id=project_id)
        dto = await handler.handle(query)
        items = [ProjectRoleResponse.model_validate(r.__dict__) for r in dto.items]
        return SuccessResponse(data=items)

    async def get_role(
        self, ws_id: str, project_id: str, role_id: str,
        caller_id: str = Depends(get_current_user_id),
        role_repo=Depends(get_project_role_repository),
        permission_checker=Depends(get_project_permission_checker),
    ) -> SuccessResponse[ProjectRoleResponse]:
        handler = GetProjectRoleHandler(role_repo=role_repo, permission_checker=permission_checker)
        query = GetProjectRoleQuery(caller_id=caller_id, role_id=role_id)
        dto = await handler.handle(query)
        return SuccessResponse(data=ProjectRoleResponse.model_validate(dto.__dict__))

    async def create_role(
        self, ws_id: str, project_id: str, body: CreateProjectRoleRequest,
        caller_id: str = Depends(get_current_user_id),
        project_repo=Depends(get_project_repository),
        role_repo=Depends(get_project_role_repository),
        permission_checker=Depends(get_project_permission_checker),
        event_bus=Depends(get_project_event_bus),
    ) -> SuccessResponse[ProjectRoleResponse]:
        handler = CreateProjectRoleHandler(
            project_repo=project_repo, role_repo=role_repo, permission_checker=permission_checker, event_bus=event_bus,
        )
        command = CreateProjectRoleCommand(
            caller_id=caller_id, project_id=project_id,
            name=body.name, permissions=body.permissions, description=body.description,
        )
        dto = await handler.handle(command)
        return SuccessResponse(data=ProjectRoleResponse.model_validate(dto.__dict__))

    async def update_role(
        self, ws_id: str, project_id: str, role_id: str, body: UpdateProjectRoleRequest,
        caller_id: str = Depends(get_current_user_id),
        role_repo=Depends(get_project_role_repository),
        permission_checker=Depends(get_project_permission_checker),
        event_bus=Depends(get_project_event_bus),
    ) -> MessageResponse:
        handler = UpdateProjectRoleHandler(
            role_repo=role_repo, permission_checker=permission_checker, event_bus=event_bus,
        )
        await handler.handle(UpdateProjectRoleCommand(
            caller_id=caller_id, project_id=project_id, role_id=role_id,
            permissions=body.permissions, description=body.description,
        ))
        return SuccessResponse(data={"message": "Роль проекта обновлена"})

    async def delete_role(
        self, ws_id: str, project_id: str, role_id: str,
        caller_id: str = Depends(get_current_user_id),
        role_repo=Depends(get_project_role_repository),
        permission_checker=Depends(get_project_permission_checker),
        event_bus=Depends(get_project_event_bus),
    ) -> MessageResponse:
        handler = DeleteProjectRoleHandler(
            role_repo=role_repo, permission_checker=permission_checker, event_bus=event_bus,
        )
        await handler.handle(DeleteProjectRoleCommand(
            caller_id=caller_id, project_id=project_id, role_id=role_id,
        ))
        return SuccessResponse(data={"message": "Роль проекта удалена"})
