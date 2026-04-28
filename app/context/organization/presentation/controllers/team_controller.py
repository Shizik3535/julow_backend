from __future__ import annotations

from fastapi import Depends

from app.shared.presentation.base_controller import BaseController
from app.shared.presentation.responses import (
    ErrorResponse,
    MessageResponse,
    SuccessResponse,
)

from app.context.organization.application.commands.create_team import (
    CreateTeamCommand,
    CreateTeamHandler,
)
from app.context.organization.application.commands.update_team import (
    UpdateTeamCommand,
    UpdateTeamHandler,
)
from app.context.organization.application.commands.deactivate_team import (
    DeactivateTeamCommand,
    DeactivateTeamHandler,
)
from app.context.organization.application.commands.reactivate_team import (
    ReactivateTeamCommand,
    ReactivateTeamHandler,
)
from app.context.organization.application.commands.add_team_member import (
    AddTeamMemberCommand,
    AddTeamMemberHandler,
)
from app.context.organization.application.commands.remove_team_member import (
    RemoveTeamMemberCommand,
    RemoveTeamMemberHandler,
)
from app.context.organization.application.queries.get_teams_by_org import (
    GetTeamsByOrgHandler,
    GetTeamsByOrgQuery,
)
from app.context.organization.application.queries.get_team import (
    GetTeamHandler,
    GetTeamQuery,
)
from app.context.organization.presentation.dependencies import (
    get_current_user_id,
    get_org_membership_repository,
    get_org_permission_checker,
    get_organization_event_bus,
    get_organization_repository,
    get_team_repository,
)
from app.context.organization.presentation.schemas.requests.create_team_request import (
    CreateTeamRequest,
)
from app.context.organization.presentation.schemas.requests.update_team_request import (
    UpdateTeamRequest,
)
from app.context.organization.presentation.schemas.responses.team_response import (
    TeamResponse,
)


class TeamController(BaseController):
    """
    Контроллер команд организации.

    Endpoint'ы:
        GET    /{org_id}/teams                                  — Список команд
        GET    /{org_id}/teams/{team_id}                        — Получить команду
        POST   /{org_id}/teams                                  — Создать команду
        PATCH  /{org_id}/teams/{team_id}                        — Обновить команду
        POST   /{org_id}/teams/{team_id}/deactivate             — Деактивировать
        POST   /{org_id}/teams/{team_id}/reactivate             — Реактивировать
        POST   /{org_id}/teams/{team_id}/members/{user_id}      — Добавить участника
        DELETE /{org_id}/teams/{team_id}/members/{user_id}      — Удалить участника
    """

    def __init__(self) -> None:
        super().__init__(prefix="/orgs", tags=["Organization / Teams"])

    def _register_routes(self) -> None:
        self._router.add_api_route(
            "/{org_id}/teams",
            self.get_teams,
            methods=["GET"],
            response_model=SuccessResponse[list[TeamResponse]],
            summary="Список команд",
            description="Возвращает список команд организации.",
            responses={
                200: {"description": "Список команд"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                404: {"description": "Организация не найдена", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{org_id}/teams/{team_id}",
            self.get_team,
            methods=["GET"],
            response_model=SuccessResponse[TeamResponse],
            summary="Получить команду",
            description="Возвращает данные команды по UUID.",
            responses={
                200: {"description": "Данные команды"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                404: {"description": "Команда не найдена", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{org_id}/teams",
            self.create_team,
            methods=["POST"],
            response_model=SuccessResponse[TeamResponse],
            status_code=201,
            summary="Создать команду",
            description="Создаёт новую команду в организации.",
            responses={
                201: {"description": "Команда создана"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Организация не найдена", "model": ErrorResponse},
                422: {"description": "Ошибка валидации", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{org_id}/teams/{team_id}",
            self.update_team,
            methods=["PATCH"],
            response_model=MessageResponse,
            summary="Обновить команду",
            description="Обновляет название, описание, лидера и/или иконку команды.",
            responses={
                200: {"description": "Команда обновлена"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Команда не найдена", "model": ErrorResponse},
                422: {"description": "Ошибка валидации", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{org_id}/teams/{team_id}/deactivate",
            self.deactivate_team,
            methods=["POST"],
            response_model=MessageResponse,
            summary="Деактивировать команду",
            description="Деактивирует команду без удаления.",
            responses={
                200: {"description": "Команда деактивирована"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Команда не найдена", "model": ErrorResponse},
                409: {"description": "Нарушение бизнес-правила", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{org_id}/teams/{team_id}/reactivate",
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
            "/{org_id}/teams/{team_id}/members/{user_id}",
            self.add_team_member,
            methods=["POST"],
            response_model=MessageResponse,
            summary="Добавить участника в команду",
            description="Добавляет участника организации в команду. Пользователь должен быть членом организации.",
            responses={
                200: {"description": "Участник добавлен"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Команда не найдена / пользователь не в организации", "model": ErrorResponse},
                409: {"description": "Участник уже в команде", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{org_id}/teams/{team_id}/members/{user_id}",
            self.remove_team_member,
            methods=["DELETE"],
            response_model=MessageResponse,
            summary="Удалить участника из команды",
            description="Удаляет участника из команды.",
            responses={
                200: {"description": "Участник удалён"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Команда не найдена", "model": ErrorResponse},
            },
        )

    # ------------------------------------------------------------------
    # Team CRUD
    # ------------------------------------------------------------------

    async def get_teams(
        self,
        org_id: str,
        caller_id: str = Depends(get_current_user_id),
        team_repo=Depends(get_team_repository),
        org_repo=Depends(get_organization_repository),
        org_permission_checker=Depends(get_org_permission_checker),
    ) -> SuccessResponse[list[TeamResponse]]:
        """Получить список команд."""
        handler = GetTeamsByOrgHandler(team_repo=team_repo, org_repo=org_repo, org_permission_checker=org_permission_checker)
        query = GetTeamsByOrgQuery(caller_id=caller_id, org_id=org_id)
        dto = await handler.handle(query)
        items = [TeamResponse.model_validate(item.model_dump()) for item in dto.items]
        return SuccessResponse(data=items)

    async def get_team(
        self,
        org_id: str,
        team_id: str,
        caller_id: str = Depends(get_current_user_id),
        team_repo=Depends(get_team_repository),
        org_permission_checker=Depends(get_org_permission_checker),
    ) -> SuccessResponse[TeamResponse]:
        """Получить команду по ID."""
        handler = GetTeamHandler(team_repo=team_repo, org_permission_checker=org_permission_checker)
        query = GetTeamQuery(caller_id=caller_id, org_id=org_id, team_id=team_id)
        dto = await handler.handle(query)
        return SuccessResponse(data=TeamResponse.model_validate(dto.model_dump()))

    async def create_team(
        self,
        org_id: str,
        body: CreateTeamRequest,
        caller_id: str = Depends(get_current_user_id),
        team_repo=Depends(get_team_repository),
        org_repo=Depends(get_organization_repository),
        org_permission_checker=Depends(get_org_permission_checker),
        event_bus=Depends(get_organization_event_bus),
    ) -> SuccessResponse[TeamResponse]:
        """Создать команду."""
        handler = CreateTeamHandler(
            team_repo=team_repo,
            org_repo=org_repo,
            org_permission_checker=org_permission_checker,
            event_bus=event_bus,
        )
        command = CreateTeamCommand(
            caller_id=caller_id,
            org_id=org_id,
            name=body.name,
            lead_id=body.lead_id,
        )
        dto = await handler.handle(command)
        return SuccessResponse(data=TeamResponse.model_validate(dto.model_dump()))

    async def update_team(
        self,
        org_id: str,
        team_id: str,
        body: UpdateTeamRequest,
        caller_id: str = Depends(get_current_user_id),
        team_repo=Depends(get_team_repository),
        org_permission_checker=Depends(get_org_permission_checker),
        event_bus=Depends(get_organization_event_bus),
    ) -> MessageResponse:
        """Обновить команду."""
        handler = UpdateTeamHandler(
            team_repo=team_repo,
            org_permission_checker=org_permission_checker,
            event_bus=event_bus,
        )
        command = UpdateTeamCommand(
            caller_id=caller_id,
            org_id=org_id,
            team_id=team_id,
            name=body.name,
            description=body.description,
            lead_id=body.lead_id,
            icon=body.icon,
        )
        await handler.handle(command)
        return MessageResponse(message="Команда обновлена")

    async def deactivate_team(
        self,
        org_id: str,
        team_id: str,
        caller_id: str = Depends(get_current_user_id),
        team_repo=Depends(get_team_repository),
        org_permission_checker=Depends(get_org_permission_checker),
        event_bus=Depends(get_organization_event_bus),
    ) -> MessageResponse:
        """Деактивировать команду."""
        handler = DeactivateTeamHandler(
            team_repo=team_repo,
            org_permission_checker=org_permission_checker,
            event_bus=event_bus,
        )
        command = DeactivateTeamCommand(
            caller_id=caller_id,
            org_id=org_id,
            team_id=team_id,
        )
        await handler.handle(command)
        return MessageResponse(message="Команда деактивирована")

    async def reactivate_team(
        self,
        org_id: str,
        team_id: str,
        caller_id: str = Depends(get_current_user_id),
        team_repo=Depends(get_team_repository),
        org_permission_checker=Depends(get_org_permission_checker),
        event_bus=Depends(get_organization_event_bus),
    ) -> MessageResponse:
        """Реактивировать команду."""
        handler = ReactivateTeamHandler(
            team_repo=team_repo,
            org_permission_checker=org_permission_checker,
            event_bus=event_bus,
        )
        command = ReactivateTeamCommand(
            caller_id=caller_id,
            org_id=org_id,
            team_id=team_id,
        )
        await handler.handle(command)
        return MessageResponse(message="Команда реактивирована")

    # ------------------------------------------------------------------
    # Team members
    # ------------------------------------------------------------------

    async def add_team_member(
        self,
        org_id: str,
        team_id: str,
        user_id: str,
        caller_id: str = Depends(get_current_user_id),
        team_repo=Depends(get_team_repository),
        membership_repo=Depends(get_org_membership_repository),
        org_permission_checker=Depends(get_org_permission_checker),
        event_bus=Depends(get_organization_event_bus),
    ) -> MessageResponse:
        """Добавить участника в команду."""
        handler = AddTeamMemberHandler(
            team_repo=team_repo,
            membership_repo=membership_repo,
            org_permission_checker=org_permission_checker,
            event_bus=event_bus,
        )
        command = AddTeamMemberCommand(
            caller_id=caller_id,
            org_id=org_id,
            team_id=team_id,
            user_id=user_id,
        )
        await handler.handle(command)
        return MessageResponse(message="Участник добавлен в команду")

    async def remove_team_member(
        self,
        org_id: str,
        team_id: str,
        user_id: str,
        caller_id: str = Depends(get_current_user_id),
        team_repo=Depends(get_team_repository),
        org_permission_checker=Depends(get_org_permission_checker),
        event_bus=Depends(get_organization_event_bus),
    ) -> MessageResponse:
        """Удалить участника из команды."""
        handler = RemoveTeamMemberHandler(
            team_repo=team_repo,
            org_permission_checker=org_permission_checker,
            event_bus=event_bus,
        )
        command = RemoveTeamMemberCommand(
            caller_id=caller_id,
            org_id=org_id,
            team_id=team_id,
            user_id=user_id,
        )
        await handler.handle(command)
        return MessageResponse(message="Участник удалён из команды")
