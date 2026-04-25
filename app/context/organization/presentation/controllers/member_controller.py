from __future__ import annotations

from fastapi import Depends

from app.shared.presentation.base_controller import BaseController
from app.shared.presentation.responses import (
    ErrorResponse,
    MessageResponse,
    SuccessResponse,
)

from app.context.organization.application.commands.add_org_member import (
    AddOrgMemberCommand,
    AddOrgMemberHandler,
)
from app.context.organization.application.commands.remove_org_member import (
    RemoveOrgMemberCommand,
    RemoveOrgMemberHandler,
)
from app.context.organization.application.commands.change_org_member_role import (
    ChangeOrgMemberRoleCommand,
    ChangeOrgMemberRoleHandler,
)
from app.context.organization.application.commands.update_org_member_display_name import (
    UpdateOrgMemberDisplayNameCommand,
    UpdateOrgMemberDisplayNameHandler,
)
from app.context.organization.application.commands.deactivate_org_member import (
    DeactivateOrgMemberCommand,
    DeactivateOrgMemberHandler,
)
from app.context.organization.application.commands.reactivate_org_member import (
    ReactivateOrgMemberCommand,
    ReactivateOrgMemberHandler,
)
from app.context.organization.application.commands.add_org_owner import (
    AddOrgOwnerCommand,
    AddOrgOwnerHandler,
)
from app.context.organization.application.commands.remove_org_owner import (
    RemoveOrgOwnerCommand,
    RemoveOrgOwnerHandler,
)
from app.context.organization.application.queries.get_org_members import (
    GetOrgMembersHandler,
    GetOrgMembersQuery,
)
from app.context.organization.application.queries.get_org_member import (
    GetOrgMemberHandler,
    GetOrgMemberQuery,
)
from app.context.organization.presentation.dependencies import (
    get_current_user_id,
    get_org_identity_user_port,
    get_org_membership_repository,
    get_org_permission_checker,
    get_org_role_repository,
    get_organization_event_bus,
    get_organization_repository,
)
from app.context.organization.presentation.schemas.requests.add_org_member_request import (
    AddOrgMemberRequest,
)
from app.context.organization.presentation.schemas.requests.add_org_owner_request import (
    AddOrgOwnerRequest,
)
from app.context.organization.presentation.schemas.requests.change_org_member_role_request import (
    ChangeOrgMemberRoleRequest,
)
from app.context.organization.presentation.schemas.requests.update_org_member_display_name_request import (
    UpdateOrgMemberDisplayNameRequest,
)
from app.context.organization.presentation.schemas.responses.org_member_response import (
    OrgMemberResponse,
)


class MemberController(BaseController):
    """
    Контроллер участников организации.

    Endpoint'ы:
        GET    /{org_id}/members                          — Список участников
        GET    /{org_id}/members/{user_id}                — Получить участника
        POST   /{org_id}/members                          — Добавить участника
        PATCH  /{org_id}/members/{user_id}/role           — Изменить роль
        PATCH  /{org_id}/members/{user_id}/display-name   — Изменить отображаемое имя
        DELETE /{org_id}/members/{user_id}                — Удалить участника
        POST   /{org_id}/members/{user_id}/deactivate     — Деактивировать
        POST   /{org_id}/members/{user_id}/reactivate     — Реактивировать
        POST   /{org_id}/owners                           — Добавить со-владельца
        DELETE /{org_id}/owners/{user_id}                 — Удалить со-владельца
    """

    def __init__(self) -> None:
        super().__init__(prefix="/orgs", tags=["Organization / Members"])

    def _register_routes(self) -> None:
        self._router.add_api_route(
            "/{org_id}/members",
            self.get_members,
            methods=["GET"],
            response_model=SuccessResponse[list[OrgMemberResponse]],
            summary="Список участников организации",
            description="Возвращает список всех участников организации.",
            responses={
                200: {"description": "Список участников"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                404: {"description": "Организация не найдена", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{org_id}/members/{user_id}",
            self.get_member,
            methods=["GET"],
            response_model=SuccessResponse[OrgMemberResponse],
            summary="Получить участника",
            description="Возвращает данные конкретного участника организации.",
            responses={
                200: {"description": "Данные участника"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                404: {"description": "Участник не найден", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{org_id}/members",
            self.add_member,
            methods=["POST"],
            response_model=MessageResponse,
            status_code=201,
            summary="Добавить участника",
            description="Добавляет пользователя в организацию с указанной ролью.",
            responses={
                201: {"description": "Участник добавлен"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Организация не найдена", "model": ErrorResponse},
                409: {"description": "Участник уже состоит / пользователь не найден", "model": ErrorResponse},
                422: {"description": "Ошибка валидации", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{org_id}/members/{user_id}/role",
            self.change_member_role,
            methods=["PATCH"],
            response_model=MessageResponse,
            summary="Изменить роль участника",
            description="Изменяет роль указанного участника организации.",
            responses={
                200: {"description": "Роль изменена"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Участник не найден", "model": ErrorResponse},
                422: {"description": "Ошибка валидации", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{org_id}/members/{user_id}/display-name",
            self.update_member_display_name,
            methods=["PATCH"],
            response_model=MessageResponse,
            summary="Изменить отображаемое имя участника",
            description="Обновляет отображаемое имя участника в рамках организации.",
            responses={
                200: {"description": "Имя обновлено"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Участник не найден", "model": ErrorResponse},
                422: {"description": "Ошибка валидации", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{org_id}/members/{user_id}",
            self.remove_member,
            methods=["DELETE"],
            response_model=MessageResponse,
            summary="Удалить участника",
            description="Удаляет участника из организации.",
            responses={
                200: {"description": "Участник удалён"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Участник не найден", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{org_id}/members/{user_id}/deactivate",
            self.deactivate_member,
            methods=["POST"],
            response_model=MessageResponse,
            summary="Деактивировать участника",
            description="Деактивирует участника организации без удаления.",
            responses={
                200: {"description": "Участник деактивирован"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Участник не найден", "model": ErrorResponse},
                409: {"description": "Нарушение бизнес-правила", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{org_id}/members/{user_id}/reactivate",
            self.reactivate_member,
            methods=["POST"],
            response_model=MessageResponse,
            summary="Реактивировать участника",
            description="Реактивирует ранее деактивированного участника.",
            responses={
                200: {"description": "Участник реактивирован"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Участник не найден", "model": ErrorResponse},
                409: {"description": "Нарушение бизнес-правила", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{org_id}/owners",
            self.add_owner,
            methods=["POST"],
            response_model=MessageResponse,
            summary="Добавить со-владельца",
            description="Назначает пользователя со-владельцем организации.",
            responses={
                200: {"description": "Со-владелец добавлен"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Организация не найдена", "model": ErrorResponse},
                409: {"description": "Нарушение бизнес-правила", "model": ErrorResponse},
                422: {"description": "Ошибка валидации", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{org_id}/owners/{user_id}",
            self.remove_owner,
            methods=["DELETE"],
            response_model=MessageResponse,
            summary="Удалить со-владельца",
            description="Снимает статус со-владельца. Минимум один владелец остаётся.",
            responses={
                200: {"description": "Со-владелец удалён"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Организация не найдена", "model": ErrorResponse},
                409: {"description": "Нельзя удалить последнего владельца", "model": ErrorResponse},
            },
        )

    # ------------------------------------------------------------------
    # Members
    # ------------------------------------------------------------------

    async def get_members(
        self,
        org_id: str,
        caller_id: str = Depends(get_current_user_id),
        membership_repo=Depends(get_org_membership_repository),
    ) -> SuccessResponse[list[OrgMemberResponse]]:
        """Получить список участников организации."""
        handler = GetOrgMembersHandler(membership_repo=membership_repo)
        query = GetOrgMembersQuery(org_id=org_id)
        dto = await handler.handle(query)
        items = [OrgMemberResponse.model_validate(item.model_dump()) for item in dto.items]
        return SuccessResponse(data=items)

    async def get_member(
        self,
        org_id: str,
        user_id: str,
        caller_id: str = Depends(get_current_user_id),
        membership_repo=Depends(get_org_membership_repository),
    ) -> SuccessResponse[OrgMemberResponse]:
        """Получить данные конкретного участника."""
        handler = GetOrgMemberHandler(membership_repo=membership_repo)
        query = GetOrgMemberQuery(org_id=org_id, user_id=user_id)
        dto = await handler.handle(query)
        return SuccessResponse(data=OrgMemberResponse.model_validate(dto.model_dump()))

    async def add_member(
        self,
        org_id: str,
        body: AddOrgMemberRequest,
        caller_id: str = Depends(get_current_user_id),
        org_repo=Depends(get_organization_repository),
        membership_repo=Depends(get_org_membership_repository),
        role_repo=Depends(get_org_role_repository),
        identity_port=Depends(get_org_identity_user_port),
        org_permission_checker=Depends(get_org_permission_checker),
        event_bus=Depends(get_organization_event_bus),
    ) -> MessageResponse:
        """Добавить участника в организацию."""
        handler = AddOrgMemberHandler(
            membership_repo=membership_repo,
            org_repo=org_repo,
            org_role_repo=role_repo,
            identity_port=identity_port,
            org_permission_checker=org_permission_checker,
            event_bus=event_bus,
        )
        command = AddOrgMemberCommand(
            caller_id=caller_id,
            org_id=org_id,
            user_id=body.user_id,
            role_id=body.role_id,
            invited_by=caller_id,
            display_name=body.display_name,
        )
        await handler.handle(command)
        return MessageResponse(message="Участник добавлен в организацию")

    async def change_member_role(
        self,
        org_id: str,
        user_id: str,
        body: ChangeOrgMemberRoleRequest,
        caller_id: str = Depends(get_current_user_id),
        membership_repo=Depends(get_org_membership_repository),
        org_permission_checker=Depends(get_org_permission_checker),
        event_bus=Depends(get_organization_event_bus),
    ) -> MessageResponse:
        """Изменить роль участника."""
        handler = ChangeOrgMemberRoleHandler(
            membership_repo=membership_repo,
            org_permission_checker=org_permission_checker,
            event_bus=event_bus,
        )
        command = ChangeOrgMemberRoleCommand(
            caller_id=caller_id,
            org_id=org_id,
            user_id=user_id,
            new_role_id=body.new_role_id,
        )
        await handler.handle(command)
        return MessageResponse(message="Роль участника изменена")

    async def update_member_display_name(
        self,
        org_id: str,
        user_id: str,
        body: UpdateOrgMemberDisplayNameRequest,
        caller_id: str = Depends(get_current_user_id),
        membership_repo=Depends(get_org_membership_repository),
        org_permission_checker=Depends(get_org_permission_checker),
        event_bus=Depends(get_organization_event_bus),
    ) -> MessageResponse:
        """Обновить отображаемое имя участника."""
        handler = UpdateOrgMemberDisplayNameHandler(
            membership_repo=membership_repo,
            org_permission_checker=org_permission_checker,
            event_bus=event_bus,
        )
        command = UpdateOrgMemberDisplayNameCommand(
            caller_id=caller_id,
            org_id=org_id,
            user_id=user_id,
            display_name=body.display_name,
        )
        await handler.handle(command)
        return MessageResponse(message="Отображаемое имя обновлено")

    async def remove_member(
        self,
        org_id: str,
        user_id: str,
        caller_id: str = Depends(get_current_user_id),
        org_repo=Depends(get_organization_repository),
        membership_repo=Depends(get_org_membership_repository),
        org_permission_checker=Depends(get_org_permission_checker),
        event_bus=Depends(get_organization_event_bus),
    ) -> MessageResponse:
        """Удалить участника из организации."""
        handler = RemoveOrgMemberHandler(
            org_repo=org_repo,
            membership_repo=membership_repo,
            org_permission_checker=org_permission_checker,
            event_bus=event_bus,
        )
        command = RemoveOrgMemberCommand(
            caller_id=caller_id,
            org_id=org_id,
            user_id=user_id,
        )
        await handler.handle(command)
        return MessageResponse(message="Участник удалён из организации")

    async def deactivate_member(
        self,
        org_id: str,
        user_id: str,
        caller_id: str = Depends(get_current_user_id),
        org_repo=Depends(get_organization_repository),
        membership_repo=Depends(get_org_membership_repository),
        org_permission_checker=Depends(get_org_permission_checker),
        event_bus=Depends(get_organization_event_bus),
    ) -> MessageResponse:
        """Деактивировать участника."""
        handler = DeactivateOrgMemberHandler(
            org_repo=org_repo,
            membership_repo=membership_repo,
            org_permission_checker=org_permission_checker,
            event_bus=event_bus,
        )
        command = DeactivateOrgMemberCommand(
            caller_id=caller_id,
            org_id=org_id,
            user_id=user_id,
        )
        await handler.handle(command)
        return MessageResponse(message="Участник деактивирован")

    async def reactivate_member(
        self,
        org_id: str,
        user_id: str,
        caller_id: str = Depends(get_current_user_id),
        membership_repo=Depends(get_org_membership_repository),
        org_permission_checker=Depends(get_org_permission_checker),
        event_bus=Depends(get_organization_event_bus),
    ) -> MessageResponse:
        """Реактивировать участника."""
        handler = ReactivateOrgMemberHandler(
            membership_repo=membership_repo,
            org_permission_checker=org_permission_checker,
            event_bus=event_bus,
        )
        command = ReactivateOrgMemberCommand(
            caller_id=caller_id,
            org_id=org_id,
            user_id=user_id,
        )
        await handler.handle(command)
        return MessageResponse(message="Участник реактивирован")

    # ------------------------------------------------------------------
    # Owners
    # ------------------------------------------------------------------

    async def add_owner(
        self,
        org_id: str,
        body: AddOrgOwnerRequest,
        caller_id: str = Depends(get_current_user_id),
        org_repo=Depends(get_organization_repository),
        org_permission_checker=Depends(get_org_permission_checker),
        event_bus=Depends(get_organization_event_bus),
    ) -> MessageResponse:
        """Добавить со-владельца."""
        handler = AddOrgOwnerHandler(
            org_repo=org_repo,
            org_permission_checker=org_permission_checker,
            event_bus=event_bus,
        )
        command = AddOrgOwnerCommand(
            caller_id=caller_id,
            org_id=org_id,
            user_id=body.user_id,
        )
        await handler.handle(command)
        return MessageResponse(message="Со-владелец добавлен")

    async def remove_owner(
        self,
        org_id: str,
        user_id: str,
        caller_id: str = Depends(get_current_user_id),
        org_repo=Depends(get_organization_repository),
        org_permission_checker=Depends(get_org_permission_checker),
        event_bus=Depends(get_organization_event_bus),
    ) -> MessageResponse:
        """Удалить со-владельца."""
        handler = RemoveOrgOwnerHandler(
            org_repo=org_repo,
            org_permission_checker=org_permission_checker,
            event_bus=event_bus,
        )
        command = RemoveOrgOwnerCommand(
            caller_id=caller_id,
            org_id=org_id,
            user_id=user_id,
        )
        await handler.handle(command)
        return MessageResponse(message="Со-владелец удалён")
