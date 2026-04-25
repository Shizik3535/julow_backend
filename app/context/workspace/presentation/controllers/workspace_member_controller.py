from __future__ import annotations

from fastapi import Depends, Query

from app.shared.presentation.base_controller import BaseController
from app.shared.presentation.responses import (
    ErrorResponse,
    MessageResponse,
    PaginatedResponse,
    SuccessResponse,
)

from app.context.workspace.application.commands.add_workspace_member import (
    AddWorkspaceMemberCommand,
    AddWorkspaceMemberHandler,
)
from app.context.workspace.application.commands.remove_workspace_member import (
    RemoveWorkspaceMemberCommand,
    RemoveWorkspaceMemberHandler,
)
from app.context.workspace.application.commands.deactivate_workspace_member import (
    DeactivateWorkspaceMemberCommand,
    DeactivateWorkspaceMemberHandler,
)
from app.context.workspace.application.commands.reactivate_workspace_member import (
    ReactivateWorkspaceMemberCommand,
    ReactivateWorkspaceMemberHandler,
)
from app.context.workspace.application.commands.change_workspace_member_role import (
    ChangeWorkspaceMemberRoleCommand,
    ChangeWorkspaceMemberRoleHandler,
)
from app.context.workspace.application.commands.update_workspace_member_display_name import (
    UpdateWorkspaceMemberDisplayNameCommand,
    UpdateWorkspaceMemberDisplayNameHandler,
)
from app.context.workspace.application.queries.get_workspace_members import (
    GetWorkspaceMembersHandler,
    GetWorkspaceMembersQuery,
)
from app.context.workspace.application.queries.get_workspace_member import (
    GetWorkspaceMemberHandler,
    GetWorkspaceMemberQuery,
)
from app.context.workspace.presentation.dependencies import (
    get_current_user_id,
    get_workspace_event_bus,
    get_workspace_membership_repository,
    get_workspace_permission_checker,
    get_workspace_repository,
    get_ws_identity_user_port,
)
from app.context.workspace.presentation.schemas.requests.add_workspace_member_request import AddWorkspaceMemberRequest
from app.context.workspace.presentation.schemas.requests.change_workspace_member_role_request import (
    ChangeWorkspaceMemberRoleRequest,
)
from app.context.workspace.presentation.schemas.requests.update_workspace_member_display_name_request import (
    UpdateWorkspaceMemberDisplayNameRequest,
)
from app.context.workspace.presentation.schemas.responses.workspace_member_response import WorkspaceMemberResponse


class WorkspaceMemberController(BaseController):
    """
    Контроллер участников workspace.

    Endpoint'ы:
        GET    /{ws_id}/members                           — Список участников
        GET    /{ws_id}/members/{user_id}                 — Получить участника
        POST   /{ws_id}/members                           — Добавить участника
        PATCH  /{ws_id}/members/{user_id}/role             — Изменить роль
        PATCH  /{ws_id}/members/{user_id}/display-name    — Изменить отображаемое имя
        DELETE /{ws_id}/members/{user_id}                  — Удалить участника
        POST   /{ws_id}/members/{user_id}/deactivate       — Деактивировать
        POST   /{ws_id}/members/{user_id}/reactivate       — Реактивировать
    """

    def __init__(self) -> None:
        super().__init__(prefix="/workspaces", tags=["Workspace / Members"])

    def _register_routes(self) -> None:
        self._router.add_api_route(
            "/{ws_id}/members",
            self.get_members,
            methods=["GET"],
            response_model=PaginatedResponse[WorkspaceMemberResponse],
            summary="Список участников workspace",
            description="Возвращает пагинированный список участников workspace.",
            responses={
                200: {"description": "Список участников"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Workspace не найден", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{ws_id}/members/{user_id}",
            self.get_member,
            methods=["GET"],
            response_model=SuccessResponse[WorkspaceMemberResponse],
            summary="Получить участника workspace",
            description="Возвращает данные участника workspace по user_id.",
            responses={
                200: {"description": "Данные участника"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Участник не найден", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{ws_id}/members",
            self.add_member,
            methods=["POST"],
            response_model=MessageResponse,
            status_code=201,
            summary="Добавить участника в workspace",
            description="Добавляет пользователя как участника в workspace с указанной ролью.",
            responses={
                201: {"description": "Участник добавлен"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Workspace не найден", "model": ErrorResponse},
                409: {"description": "Участник уже существует", "model": ErrorResponse},
                422: {"description": "Ошибка валидации", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{ws_id}/members/{user_id}/role",
            self.change_member_role,
            methods=["PATCH"],
            response_model=MessageResponse,
            summary="Изменить роль участника",
            description="Изменяет роль участника workspace.",
            responses={
                200: {"description": "Роль изменена"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Участник не найден", "model": ErrorResponse},
                409: {"description": "Нарушение бизнес-правила", "model": ErrorResponse},
                422: {"description": "Ошибка валидации", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{ws_id}/members/{user_id}/display-name",
            self.update_member_display_name,
            methods=["PATCH"],
            response_model=MessageResponse,
            summary="Изменить отображаемое имя участника",
            description="Обновляет отображаемое имя участника в рамках workspace.",
            responses={
                200: {"description": "Имя обновлено"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Участник не найден", "model": ErrorResponse},
                422: {"description": "Ошибка валидации", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{ws_id}/members/{user_id}",
            self.remove_member,
            methods=["DELETE"],
            response_model=MessageResponse,
            summary="Удалить участника из workspace",
            description="Удаляет участника из workspace.",
            responses={
                200: {"description": "Участник удалён"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Участник не найден", "model": ErrorResponse},
                409: {"description": "Нельзя удалить последнего владельца", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{ws_id}/members/{user_id}/deactivate",
            self.deactivate_member,
            methods=["POST"],
            response_model=MessageResponse,
            summary="Деактивировать участника",
            description="Деактивирует участника workspace без удаления.",
            responses={
                200: {"description": "Участник деактивирован"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Участник не найден", "model": ErrorResponse},
                409: {"description": "Нельзя деактивировать последнего владельца", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{ws_id}/members/{user_id}/reactivate",
            self.reactivate_member,
            methods=["POST"],
            response_model=MessageResponse,
            summary="Реактивировать участника",
            description="Реактивирует ранее деактивированного участника workspace.",
            responses={
                200: {"description": "Участник реактивирован"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Участник не найден", "model": ErrorResponse},
                409: {"description": "Нарушение бизнес-правила", "model": ErrorResponse},
            },
        )

    # ------------------------------------------------------------------
    # Workspace Members
    # ------------------------------------------------------------------

    async def get_members(
        self,
        ws_id: str,
        offset: int = Query(default=0, ge=0, description="Смещение пагинации"),
        limit: int = Query(default=100, ge=1, le=500, description="Размер страницы"),
        caller_id: str = Depends(get_current_user_id),
        membership_repo=Depends(get_workspace_membership_repository),
        permission_checker=Depends(get_workspace_permission_checker),
    ) -> PaginatedResponse[WorkspaceMemberResponse]:
        """Список участников workspace."""
        handler = GetWorkspaceMembersHandler(
            membership_repo=membership_repo,
            permission_checker=permission_checker,
        )
        query = GetWorkspaceMembersQuery(caller_id=caller_id, workspace_id=ws_id)
        dto = await handler.handle(query)
        items = [WorkspaceMemberResponse.model_validate(item.model_dump()) for item in dto.items]
        page = (offset // max(limit, 1)) + 1
        return PaginatedResponse(items=items, total=dto.total, page=page, page_size=limit)

    async def get_member(
        self,
        ws_id: str,
        user_id: str,
        caller_id: str = Depends(get_current_user_id),
        membership_repo=Depends(get_workspace_membership_repository),
        permission_checker=Depends(get_workspace_permission_checker),
    ) -> SuccessResponse[WorkspaceMemberResponse]:
        """Получить участника workspace."""
        handler = GetWorkspaceMemberHandler(
            membership_repo=membership_repo,
            permission_checker=permission_checker,
        )
        query = GetWorkspaceMemberQuery(caller_id=caller_id, workspace_id=ws_id, user_id=user_id)
        dto = await handler.handle(query)
        return SuccessResponse(data=WorkspaceMemberResponse.model_validate(dto.model_dump()))

    async def add_member(
        self,
        ws_id: str,
        body: AddWorkspaceMemberRequest,
        caller_id: str = Depends(get_current_user_id),
        membership_repo=Depends(get_workspace_membership_repository),
        identity_port=Depends(get_ws_identity_user_port),
        permission_checker=Depends(get_workspace_permission_checker),
        event_bus=Depends(get_workspace_event_bus),
    ) -> MessageResponse:
        """Добавить участника в workspace."""
        handler = AddWorkspaceMemberHandler(
            membership_repo=membership_repo,
            identity_port=identity_port,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        command = AddWorkspaceMemberCommand(
            caller_id=caller_id,
            workspace_id=ws_id,
            user_id=body.user_id,
            role_id=body.role_id,
            source=body.source,
            display_name=body.display_name,
        )
        await handler.handle(command)
        return SuccessResponse(data={"message": "Участник добавлен в workspace"})

    async def change_member_role(
        self,
        ws_id: str,
        user_id: str,
        body: ChangeWorkspaceMemberRoleRequest,
        caller_id: str = Depends(get_current_user_id),
        membership_repo=Depends(get_workspace_membership_repository),
        permission_checker=Depends(get_workspace_permission_checker),
        event_bus=Depends(get_workspace_event_bus),
    ) -> MessageResponse:
        """Изменить роль участника."""
        handler = ChangeWorkspaceMemberRoleHandler(
            membership_repo=membership_repo,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        command = ChangeWorkspaceMemberRoleCommand(
            caller_id=caller_id,
            workspace_id=ws_id,
            user_id=user_id,
            new_role_id=body.new_role_id,
        )
        await handler.handle(command)
        return SuccessResponse(data={"message": "Роль участника изменена"})

    async def update_member_display_name(
        self,
        ws_id: str,
        user_id: str,
        body: UpdateWorkspaceMemberDisplayNameRequest,
        caller_id: str = Depends(get_current_user_id),
        membership_repo=Depends(get_workspace_membership_repository),
        permission_checker=Depends(get_workspace_permission_checker),
        event_bus=Depends(get_workspace_event_bus),
    ) -> MessageResponse:
        """Изменить отображаемое имя участника."""
        handler = UpdateWorkspaceMemberDisplayNameHandler(
            membership_repo=membership_repo,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        command = UpdateWorkspaceMemberDisplayNameCommand(
            caller_id=caller_id,
            workspace_id=ws_id,
            user_id=user_id,
            display_name=body.display_name,
        )
        await handler.handle(command)
        return SuccessResponse(data={"message": "Отображаемое имя обновлено"})

    async def remove_member(
        self,
        ws_id: str,
        user_id: str,
        caller_id: str = Depends(get_current_user_id),
        ws_repo=Depends(get_workspace_repository),
        membership_repo=Depends(get_workspace_membership_repository),
        permission_checker=Depends(get_workspace_permission_checker),
        event_bus=Depends(get_workspace_event_bus),
    ) -> MessageResponse:
        """Удалить участника из workspace."""
        handler = RemoveWorkspaceMemberHandler(
            ws_repo=ws_repo,
            membership_repo=membership_repo,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        command = RemoveWorkspaceMemberCommand(
            caller_id=caller_id,
            workspace_id=ws_id,
            user_id=user_id,
        )
        await handler.handle(command)
        return SuccessResponse(data={"message": "Участник удалён из workspace"})

    async def deactivate_member(
        self,
        ws_id: str,
        user_id: str,
        caller_id: str = Depends(get_current_user_id),
        ws_repo=Depends(get_workspace_repository),
        membership_repo=Depends(get_workspace_membership_repository),
        permission_checker=Depends(get_workspace_permission_checker),
        event_bus=Depends(get_workspace_event_bus),
    ) -> MessageResponse:
        """Деактивировать участника workspace."""
        handler = DeactivateWorkspaceMemberHandler(
            ws_repo=ws_repo,
            membership_repo=membership_repo,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        command = DeactivateWorkspaceMemberCommand(
            caller_id=caller_id,
            workspace_id=ws_id,
            user_id=user_id,
        )
        await handler.handle(command)
        return SuccessResponse(data={"message": "Участник деактивирован"})

    async def reactivate_member(
        self,
        ws_id: str,
        user_id: str,
        caller_id: str = Depends(get_current_user_id),
        membership_repo=Depends(get_workspace_membership_repository),
        permission_checker=Depends(get_workspace_permission_checker),
        event_bus=Depends(get_workspace_event_bus),
    ) -> MessageResponse:
        """Реактивировать участника workspace."""
        handler = ReactivateWorkspaceMemberHandler(
            membership_repo=membership_repo,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        command = ReactivateWorkspaceMemberCommand(
            caller_id=caller_id,
            workspace_id=ws_id,
            user_id=user_id,
        )
        await handler.handle(command)
        return SuccessResponse(data={"message": "Участник реактивирован"})
