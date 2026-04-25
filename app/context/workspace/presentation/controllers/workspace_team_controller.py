from __future__ import annotations

from fastapi import Depends, Query

from app.shared.presentation.base_controller import BaseController
from app.shared.presentation.responses import (
    ErrorResponse,
    MessageResponse,
    PaginatedResponse,
    SuccessResponse,
)

from app.context.workspace.application.commands.create_workspace_team import (
    CreateWorkspaceTeamCommand,
    CreateWorkspaceTeamHandler,
)
from app.context.workspace.application.commands.update_workspace_team import (
    UpdateWorkspaceTeamCommand,
    UpdateWorkspaceTeamHandler,
)
from app.context.workspace.application.commands.deactivate_workspace_team import (
    DeactivateWorkspaceTeamCommand,
    DeactivateWorkspaceTeamHandler,
)
from app.context.workspace.application.commands.reactivate_workspace_team import (
    ReactivateWorkspaceTeamCommand,
    ReactivateWorkspaceTeamHandler,
)
from app.context.workspace.application.commands.add_workspace_team_member import (
    AddWorkspaceTeamMemberCommand,
    AddWorkspaceTeamMemberHandler,
)
from app.context.workspace.application.commands.remove_workspace_team_member import (
    RemoveWorkspaceTeamMemberCommand,
    RemoveWorkspaceTeamMemberHandler,
)
from app.context.workspace.application.queries.get_workspace_teams import (
    GetWorkspaceTeamsHandler,
    GetWorkspaceTeamsQuery,
)
from app.context.workspace.application.queries.get_workspace_team import (
    GetWorkspaceTeamHandler,
    GetWorkspaceTeamQuery,
)
from app.context.workspace.presentation.dependencies import (
    get_current_user_id,
    get_workspace_event_bus,
    get_workspace_membership_repository,
    get_workspace_permission_checker,
    get_workspace_repository,
    get_workspace_team_repository,
)
from app.context.workspace.presentation.schemas.requests.create_workspace_team_request import CreateWorkspaceTeamRequest
from app.context.workspace.presentation.schemas.requests.update_workspace_team_request import UpdateWorkspaceTeamRequest
from app.context.workspace.presentation.schemas.responses.workspace_team_response import WorkspaceTeamResponse


class WorkspaceTeamController(BaseController):
    """
    Контроллер команд workspace.

    Endpoint'ы:
        GET    /{ws_id}/teams                                — Список команд
        GET    /{ws_id}/teams/{team_id}                      — Получить команду
        POST   /{ws_id}/teams                                — Создать команду
        PATCH  /{ws_id}/teams/{team_id}                      — Обновить команду
        POST   /{ws_id}/teams/{team_id}/deactivate           — Деактивировать
        POST   /{ws_id}/teams/{team_id}/reactivate           — Реактивировать
        POST   /{ws_id}/teams/{team_id}/members/{user_id}    — Добавить участника
        DELETE /{ws_id}/teams/{team_id}/members/{user_id}    — Удалить участника
    """

    def __init__(self) -> None:
        super().__init__(prefix="/workspaces", tags=["Workspace / Teams"])

    def _register_routes(self) -> None:
        self._router.add_api_route(
            "/{ws_id}/teams",
            self.get_teams,
            methods=["GET"],
            response_model=PaginatedResponse[WorkspaceTeamResponse],
            summary="Список команд workspace",
            description="Возвращает пагинированный список команд workspace.",
            responses={
                200: {"description": "Список команд"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Workspace не найден", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{ws_id}/teams/{team_id}",
            self.get_team,
            methods=["GET"],
            response_model=SuccessResponse[WorkspaceTeamResponse],
            summary="Получить команду workspace",
            description="Возвращает данные команды по UUID.",
            responses={
                200: {"description": "Данные команды"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Команда не найдена", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{ws_id}/teams",
            self.create_team,
            methods=["POST"],
            response_model=SuccessResponse[WorkspaceTeamResponse],
            status_code=201,
            summary="Создать команду в workspace",
            description="Создаёт новую команду в workspace.",
            responses={
                201: {"description": "Команда создана"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Workspace не найден", "model": ErrorResponse},
                409: {"description": "Команда с таким именем уже существует", "model": ErrorResponse},
                422: {"description": "Ошибка валидации", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{ws_id}/teams/{team_id}",
            self.update_team,
            methods=["PATCH"],
            response_model=MessageResponse,
            summary="Обновить команду workspace",
            description="Обновляет название, описание, лидера или иконку команды.",
            responses={
                200: {"description": "Команда обновлена"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Команда не найдена", "model": ErrorResponse},
                422: {"description": "Ошибка валидации", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{ws_id}/teams/{team_id}/deactivate",
            self.deactivate_team,
            methods=["POST"],
            response_model=MessageResponse,
            summary="Деактивировать команду",
            description="Деактивирует команду workspace.",
            responses={
                200: {"description": "Команда деактивирована"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Команда не найдена", "model": ErrorResponse},
                409: {"description": "Нарушение бизнес-правила", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{ws_id}/teams/{team_id}/reactivate",
            self.reactivate_team,
            methods=["POST"],
            response_model=MessageResponse,
            summary="Реактивировать команду",
            description="Реактивирует ранее деактивированную команду.",
            responses={
                200: {"description": "Команда реактивирована"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Команда не найдена", "model": ErrorResponse},
                409: {"description": "Нарушение бизнес-правила", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{ws_id}/teams/{team_id}/members/{user_id}",
            self.add_team_member,
            methods=["POST"],
            response_model=MessageResponse,
            summary="Добавить участника в команду",
            description="Добавляет участника workspace в команду.",
            responses={
                200: {"description": "Участник добавлен в команду"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Команда или участник не найдены", "model": ErrorResponse},
                409: {"description": "Участник уже в команде", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{ws_id}/teams/{team_id}/members/{user_id}",
            self.remove_team_member,
            methods=["DELETE"],
            response_model=MessageResponse,
            summary="Удалить участника из команды",
            description="Удаляет участника из команды workspace.",
            responses={
                200: {"description": "Участник удалён из команды"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Команда не найдена", "model": ErrorResponse},
                409: {"description": "Нарушение бизнес-правила", "model": ErrorResponse},
            },
        )

    # ------------------------------------------------------------------
    # Workspace Teams
    # ------------------------------------------------------------------

    async def get_teams(
        self,
        ws_id: str,
        offset: int = Query(default=0, ge=0, description="Смещение пагинации"),
        limit: int = Query(default=100, ge=1, le=500, description="Размер страницы"),
        caller_id: str = Depends(get_current_user_id),
        team_repo=Depends(get_workspace_team_repository),
        ws_repo=Depends(get_workspace_repository),
        permission_checker=Depends(get_workspace_permission_checker),
    ) -> PaginatedResponse[WorkspaceTeamResponse]:
        """Список команд workspace."""
        handler = GetWorkspaceTeamsHandler(
            team_repo=team_repo,
            ws_repo=ws_repo,
            permission_checker=permission_checker,
        )
        query = GetWorkspaceTeamsQuery(caller_id=caller_id, workspace_id=ws_id)
        dto = await handler.handle(query)
        items = [WorkspaceTeamResponse.model_validate(item.model_dump()) for item in dto.items]
        page = (offset // max(limit, 1)) + 1
        return PaginatedResponse(items=items, total=dto.total, page=page, page_size=limit)

    async def get_team(
        self,
        ws_id: str,
        team_id: str,
        caller_id: str = Depends(get_current_user_id),
        team_repo=Depends(get_workspace_team_repository),
        permission_checker=Depends(get_workspace_permission_checker),
    ) -> SuccessResponse[WorkspaceTeamResponse]:
        """Получить команду workspace."""
        handler = GetWorkspaceTeamHandler(
            team_repo=team_repo,
            permission_checker=permission_checker,
        )
        query = GetWorkspaceTeamQuery(caller_id=caller_id, team_id=team_id)
        dto = await handler.handle(query)
        return SuccessResponse(data=WorkspaceTeamResponse.model_validate(dto.model_dump()))

    async def create_team(
        self,
        ws_id: str,
        body: CreateWorkspaceTeamRequest,
        caller_id: str = Depends(get_current_user_id),
        team_repo=Depends(get_workspace_team_repository),
        ws_repo=Depends(get_workspace_repository),
        permission_checker=Depends(get_workspace_permission_checker),
        event_bus=Depends(get_workspace_event_bus),
    ) -> SuccessResponse[WorkspaceTeamResponse]:
        """Создать команду в workspace."""
        handler = CreateWorkspaceTeamHandler(
            team_repo=team_repo,
            ws_repo=ws_repo,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        command = CreateWorkspaceTeamCommand(
            caller_id=caller_id,
            workspace_id=ws_id,
            name=body.name,
            lead_id=body.lead_id,
        )
        dto = await handler.handle(command)
        return SuccessResponse(data=WorkspaceTeamResponse.model_validate(dto.model_dump()))

    async def update_team(
        self,
        ws_id: str,
        team_id: str,
        body: UpdateWorkspaceTeamRequest,
        caller_id: str = Depends(get_current_user_id),
        team_repo=Depends(get_workspace_team_repository),
        permission_checker=Depends(get_workspace_permission_checker),
        event_bus=Depends(get_workspace_event_bus),
    ) -> MessageResponse:
        """Обновить команду workspace."""
        handler = UpdateWorkspaceTeamHandler(
            team_repo=team_repo,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        command = UpdateWorkspaceTeamCommand(
            caller_id=caller_id,
            team_id=team_id,
            name=body.name,
            description=body.description,
            lead_id=body.lead_id,
            icon_url=body.icon_url,
        )
        await handler.handle(command)
        return SuccessResponse(data={"message": "Команда обновлена"})

    async def deactivate_team(
        self,
        ws_id: str,
        team_id: str,
        caller_id: str = Depends(get_current_user_id),
        team_repo=Depends(get_workspace_team_repository),
        permission_checker=Depends(get_workspace_permission_checker),
        event_bus=Depends(get_workspace_event_bus),
    ) -> MessageResponse:
        """Деактивировать команду."""
        handler = DeactivateWorkspaceTeamHandler(
            team_repo=team_repo,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        command = DeactivateWorkspaceTeamCommand(caller_id=caller_id, team_id=team_id)
        await handler.handle(command)
        return SuccessResponse(data={"message": "Команда деактивирована"})

    async def reactivate_team(
        self,
        ws_id: str,
        team_id: str,
        caller_id: str = Depends(get_current_user_id),
        team_repo=Depends(get_workspace_team_repository),
        permission_checker=Depends(get_workspace_permission_checker),
        event_bus=Depends(get_workspace_event_bus),
    ) -> MessageResponse:
        """Реактивировать команду."""
        handler = ReactivateWorkspaceTeamHandler(
            team_repo=team_repo,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        command = ReactivateWorkspaceTeamCommand(caller_id=caller_id, team_id=team_id)
        await handler.handle(command)
        return SuccessResponse(data={"message": "Команда реактивирована"})

    # ------------------------------------------------------------------
    # Team Members
    # ------------------------------------------------------------------

    async def add_team_member(
        self,
        ws_id: str,
        team_id: str,
        user_id: str,
        caller_id: str = Depends(get_current_user_id),
        team_repo=Depends(get_workspace_team_repository),
        membership_repo=Depends(get_workspace_membership_repository),
        permission_checker=Depends(get_workspace_permission_checker),
        event_bus=Depends(get_workspace_event_bus),
    ) -> MessageResponse:
        """Добавить участника в команду."""
        handler = AddWorkspaceTeamMemberHandler(
            team_repo=team_repo,
            membership_repo=membership_repo,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        command = AddWorkspaceTeamMemberCommand(
            caller_id=caller_id,
            team_id=team_id,
            user_id=user_id,
        )
        await handler.handle(command)
        return SuccessResponse(data={"message": "Участник добавлен в команду"})

    async def remove_team_member(
        self,
        ws_id: str,
        team_id: str,
        user_id: str,
        caller_id: str = Depends(get_current_user_id),
        team_repo=Depends(get_workspace_team_repository),
        permission_checker=Depends(get_workspace_permission_checker),
        event_bus=Depends(get_workspace_event_bus),
    ) -> MessageResponse:
        """Удалить участника из команды."""
        handler = RemoveWorkspaceTeamMemberHandler(
            team_repo=team_repo,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        command = RemoveWorkspaceTeamMemberCommand(
            caller_id=caller_id,
            team_id=team_id,
            user_id=user_id,
        )
        await handler.handle(command)
        return SuccessResponse(data={"message": "Участник удалён из команды"})
