from __future__ import annotations

from fastapi import Depends

from app.shared.presentation.base_controller import BaseController
from app.shared.presentation.responses import ErrorResponse, MessageResponse, SuccessResponse

from app.context.project.application.commands.add_project_member import (
    AddProjectMemberCommand,
    AddProjectMemberHandler,
)
from app.context.project.application.commands.change_project_member_role import (
    ChangeProjectMemberRoleCommand,
    ChangeProjectMemberRoleHandler,
)
from app.context.project.application.commands.remove_project_member import (
    RemoveProjectMemberCommand,
    RemoveProjectMemberHandler,
)
from app.context.project.application.commands.deactivate_project_member import (
    DeactivateProjectMemberCommand,
    DeactivateProjectMemberHandler,
)
from app.context.project.application.commands.reactivate_project_member import (
    ReactivateProjectMemberCommand,
    ReactivateProjectMemberHandler,
)
from app.context.project.application.queries.get_project_members import (
    GetProjectMembersHandler,
    GetProjectMembersQuery,
)
from app.context.project.application.queries.get_project_member import (
    GetProjectMemberHandler,
    GetProjectMemberQuery,
)
from app.context.project.presentation.dependencies import (
    get_current_user_id,
    get_project_event_bus,
    get_project_identity_user_port,
    get_project_membership_repository,
    get_project_permission_checker,
    get_project_repository,
    get_project_role_repository,
    get_project_workspace_membership_port,
)
from app.context.project.presentation.schemas.requests.add_project_member_request import (
    AddProjectMemberRequest,
)
from app.context.project.presentation.schemas.requests.change_project_member_role_request import (
    ChangeProjectMemberRoleRequest,
)
from app.context.project.presentation.schemas.responses.project_member_response import (
    ProjectMemberResponse,
)


class ProjectMemberController(BaseController):
    """
    Контроллер участников проекта.

    Endpoint'ы:
        GET    /{project_id}/members                        — Список участников
        GET    /{project_id}/members/{user_id}              — Получить участника
        POST   /{project_id}/members                        — Добавить участника
        PATCH  /{project_id}/members/{user_id}/role         — Изменить роль
        DELETE /{project_id}/members/{user_id}              — Удалить участника
        POST   /{project_id}/members/{user_id}/deactivate   — Деактивировать
        POST   /{project_id}/members/{user_id}/reactivate   — Реактивировать
    """

    def __init__(self) -> None:
        super().__init__(prefix="/workspaces/{ws_id}/projects", tags=["Project / Members"])

    def _register_routes(self) -> None:
        self._router.add_api_route(
            "/{project_id}/members", self.list_members, methods=["GET"],
            response_model=SuccessResponse[list[ProjectMemberResponse]],
            summary="Список участников проекта",
        )
        self._router.add_api_route(
            "/{project_id}/members/{user_id}", self.get_member, methods=["GET"],
            response_model=SuccessResponse[ProjectMemberResponse],
            summary="Получить участника проекта",
            responses={404: {"model": ErrorResponse}},
        )
        self._router.add_api_route(
            "/{project_id}/members", self.add_member, methods=["POST"],
            response_model=MessageResponse, status_code=201,
            summary="Добавить участника в проект",
        )
        self._router.add_api_route(
            "/{project_id}/members/{user_id}/role", self.change_member_role, methods=["PATCH"],
            response_model=MessageResponse, summary="Изменить роль участника",
        )
        self._router.add_api_route(
            "/{project_id}/members/{user_id}", self.remove_member, methods=["DELETE"],
            response_model=MessageResponse, summary="Удалить участника из проекта",
        )
        self._router.add_api_route(
            "/{project_id}/members/{user_id}/deactivate", self.deactivate_member, methods=["POST"],
            response_model=MessageResponse, summary="Деактивировать участника",
        )
        self._router.add_api_route(
            "/{project_id}/members/{user_id}/reactivate", self.reactivate_member, methods=["POST"],
            response_model=MessageResponse, summary="Реактивировать участника",
        )

    async def list_members(
        self, ws_id: str, project_id: str,
        caller_id: str = Depends(get_current_user_id),
        membership_repo=Depends(get_project_membership_repository),
        permission_checker=Depends(get_project_permission_checker),
    ) -> SuccessResponse[list[ProjectMemberResponse]]:
        handler = GetProjectMembersHandler(membership_repo=membership_repo, permission_checker=permission_checker)
        query = GetProjectMembersQuery(caller_id=caller_id, project_id=project_id)
        dto = await handler.handle(query)
        items = [ProjectMemberResponse.model_validate(m.__dict__) for m in dto.items]
        return SuccessResponse(data=items)

    async def get_member(
        self, ws_id: str, project_id: str, user_id: str,
        caller_id: str = Depends(get_current_user_id),
        membership_repo=Depends(get_project_membership_repository),
        permission_checker=Depends(get_project_permission_checker),
    ) -> SuccessResponse[ProjectMemberResponse]:
        handler = GetProjectMemberHandler(membership_repo=membership_repo, permission_checker=permission_checker)
        query = GetProjectMemberQuery(caller_id=caller_id, project_id=project_id, user_id=user_id)
        dto = await handler.handle(query)
        return SuccessResponse(data=ProjectMemberResponse.model_validate(dto.__dict__))

    async def add_member(
        self, ws_id: str, project_id: str, body: AddProjectMemberRequest,
        caller_id: str = Depends(get_current_user_id),
        project_repo=Depends(get_project_repository),
        membership_repo=Depends(get_project_membership_repository),
        role_repo=Depends(get_project_role_repository),
        identity_port=Depends(get_project_identity_user_port),
        workspace_membership_port=Depends(get_project_workspace_membership_port),
        permission_checker=Depends(get_project_permission_checker),
        event_bus=Depends(get_project_event_bus),
    ) -> MessageResponse:
        handler = AddProjectMemberHandler(
            project_repo=project_repo, membership_repo=membership_repo,
            role_repo=role_repo,
            identity_port=identity_port, workspace_membership_port=workspace_membership_port,
            permission_checker=permission_checker, event_bus=event_bus,
        )
        await handler.handle(AddProjectMemberCommand(
            caller_id=caller_id, project_id=project_id,
            user_id=body.user_id, role_id=body.role_id,
            invited_by=caller_id, membership_type=body.membership_type,
        ))
        return SuccessResponse(data={"message": "Участник добавлен в проект"})

    async def change_member_role(
        self, ws_id: str, project_id: str, user_id: str, body: ChangeProjectMemberRoleRequest,
        caller_id: str = Depends(get_current_user_id),
        membership_repo=Depends(get_project_membership_repository),
        permission_checker=Depends(get_project_permission_checker),
        event_bus=Depends(get_project_event_bus),
    ) -> MessageResponse:
        handler = ChangeProjectMemberRoleHandler(
            membership_repo=membership_repo, permission_checker=permission_checker, event_bus=event_bus,
        )
        await handler.handle(ChangeProjectMemberRoleCommand(
            caller_id=caller_id, project_id=project_id,
            user_id=user_id, new_role_id=body.new_role_id,
        ))
        return SuccessResponse(data={"message": "Роль участника изменена"})

    async def remove_member(
        self, ws_id: str, project_id: str, user_id: str,
        caller_id: str = Depends(get_current_user_id),
        project_repo=Depends(get_project_repository),
        membership_repo=Depends(get_project_membership_repository),
        permission_checker=Depends(get_project_permission_checker),
        event_bus=Depends(get_project_event_bus),
    ) -> MessageResponse:
        handler = RemoveProjectMemberHandler(
            project_repo=project_repo, membership_repo=membership_repo,
            permission_checker=permission_checker, event_bus=event_bus,
        )
        await handler.handle(RemoveProjectMemberCommand(
            caller_id=caller_id, project_id=project_id, user_id=user_id,
        ))
        return SuccessResponse(data={"message": "Участник удалён из проекта"})

    async def deactivate_member(
        self, ws_id: str, project_id: str, user_id: str,
        caller_id: str = Depends(get_current_user_id),
        project_repo=Depends(get_project_repository),
        membership_repo=Depends(get_project_membership_repository),
        permission_checker=Depends(get_project_permission_checker),
        event_bus=Depends(get_project_event_bus),
    ) -> MessageResponse:
        handler = DeactivateProjectMemberHandler(
            project_repo=project_repo, membership_repo=membership_repo,
            permission_checker=permission_checker, event_bus=event_bus,
        )
        await handler.handle(DeactivateProjectMemberCommand(
            caller_id=caller_id, project_id=project_id, user_id=user_id,
        ))
        return SuccessResponse(data={"message": "Участник деактивирован"})

    async def reactivate_member(
        self, ws_id: str, project_id: str, user_id: str,
        caller_id: str = Depends(get_current_user_id),
        membership_repo=Depends(get_project_membership_repository),
        permission_checker=Depends(get_project_permission_checker),
        event_bus=Depends(get_project_event_bus),
    ) -> MessageResponse:
        handler = ReactivateProjectMemberHandler(
            membership_repo=membership_repo, permission_checker=permission_checker, event_bus=event_bus,
        )
        await handler.handle(ReactivateProjectMemberCommand(
            caller_id=caller_id, project_id=project_id, user_id=user_id,
        ))
        return SuccessResponse(data={"message": "Участник реактивирован"})
