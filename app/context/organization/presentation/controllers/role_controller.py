from __future__ import annotations

from fastapi import Depends, Query

from app.shared.presentation.base_controller import BaseController
from app.shared.presentation.responses import (
    ErrorResponse,
    MessageResponse,
    SuccessResponse,
)

from app.context.organization.application.commands.create_org_role import (
    CreateOrgRoleCommand,
    CreateOrgRoleHandler,
)
from app.context.organization.application.commands.update_org_role import (
    UpdateOrgRoleCommand,
    UpdateOrgRoleHandler,
)
from app.context.organization.application.commands.delete_org_role import (
    DeleteOrgRoleCommand,
    DeleteOrgRoleHandler,
)
from app.context.organization.application.queries.get_org_roles import (
    GetOrgRolesHandler,
    GetOrgRolesQuery,
)
from app.context.organization.application.queries.get_org_role import (
    GetOrgRoleHandler,
    GetOrgRoleQuery,
)
from app.context.organization.presentation.dependencies import (
    get_current_user_id,
    get_org_permission_checker,
    get_org_role_repository,
    get_organization_event_bus,
)
from app.context.organization.presentation.schemas.requests.create_org_role_request import (
    CreateOrgRoleRequest,
)
from app.context.organization.presentation.schemas.requests.update_org_role_request import (
    UpdateOrgRoleRequest,
)
from app.context.organization.presentation.schemas.responses.org_role_response import (
    OrgRoleResponse,
)


class RoleController(BaseController):
    """
    Контроллер ролей организации.

    Endpoint'ы:
        GET    /{org_id}/roles                  — Список ролей
        GET    /{org_id}/roles/{role_id}        — Получить роль
        POST   /{org_id}/roles                  — Создать роль
        PATCH  /{org_id}/roles/{role_id}        — Обновить роль
        DELETE /{org_id}/roles/{role_id}        — Удалить роль
    """

    def __init__(self) -> None:
        super().__init__(prefix="/orgs", tags=["Organization / Roles"])

    def _register_routes(self) -> None:
        self._router.add_api_route(
            "/{org_id}/roles",
            self.get_roles,
            methods=["GET"],
            response_model=SuccessResponse[list[OrgRoleResponse]],
            summary="Список ролей организации",
            description="Возвращает список ролей организации. Поддерживает фильтрацию по системным ролям.",
            responses={
                200: {"description": "Список ролей"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                404: {"description": "Организация не найдена", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{org_id}/roles/{role_id}",
            self.get_role,
            methods=["GET"],
            response_model=SuccessResponse[OrgRoleResponse],
            summary="Получить роль",
            description="Возвращает данные роли по UUID.",
            responses={
                200: {"description": "Данные роли"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                404: {"description": "Роль не найдена", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{org_id}/roles",
            self.create_role,
            methods=["POST"],
            response_model=SuccessResponse[OrgRoleResponse],
            status_code=201,
            summary="Создать кастомную роль",
            description="Создаёт новую кастомную роль в организации с указанными разрешениями.",
            responses={
                201: {"description": "Роль создана"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Организация не найдена", "model": ErrorResponse},
                422: {"description": "Ошибка валидации", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{org_id}/roles/{role_id}",
            self.update_role,
            methods=["PATCH"],
            response_model=MessageResponse,
            summary="Обновить роль",
            description="Обновляет разрешения и/или описание кастомной роли.",
            responses={
                200: {"description": "Роль обновлена"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Роль не найдена", "model": ErrorResponse},
                409: {"description": "Нельзя изменить системную роль", "model": ErrorResponse},
                422: {"description": "Ошибка валидации", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{org_id}/roles/{role_id}",
            self.delete_role,
            methods=["DELETE"],
            response_model=MessageResponse,
            summary="Удалить роль",
            description="Удаляет кастомную роль. Системные роли удалить нельзя.",
            responses={
                200: {"description": "Роль удалена"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Роль не найдена", "model": ErrorResponse},
                409: {"description": "Нельзя удалить системную роль", "model": ErrorResponse},
            },
        )

    # ------------------------------------------------------------------
    # Role CRUD
    # ------------------------------------------------------------------

    async def get_roles(
        self,
        org_id: str,
        system_only: bool = Query(default=False, description="Только системные роли"),
        caller_id: str = Depends(get_current_user_id),
        role_repo=Depends(get_org_role_repository),
    ) -> SuccessResponse[list[OrgRoleResponse]]:
        """Получить список ролей организации."""
        handler = GetOrgRolesHandler(role_repo=role_repo)
        query = GetOrgRolesQuery(org_id=org_id, system_only=system_only)
        dto = await handler.handle(query)
        items = [OrgRoleResponse.model_validate(item.model_dump()) for item in dto.items]
        return SuccessResponse(data=items)

    async def get_role(
        self,
        org_id: str,
        role_id: str,
        caller_id: str = Depends(get_current_user_id),
        role_repo=Depends(get_org_role_repository),
    ) -> SuccessResponse[OrgRoleResponse]:
        """Получить роль по ID."""
        handler = GetOrgRoleHandler(role_repo=role_repo)
        query = GetOrgRoleQuery(role_id=role_id)
        dto = await handler.handle(query)
        return SuccessResponse(data=OrgRoleResponse.model_validate(dto.model_dump()))

    async def create_role(
        self,
        org_id: str,
        body: CreateOrgRoleRequest,
        caller_id: str = Depends(get_current_user_id),
        role_repo=Depends(get_org_role_repository),
        org_permission_checker=Depends(get_org_permission_checker),
        event_bus=Depends(get_organization_event_bus),
    ) -> SuccessResponse[OrgRoleResponse]:
        """Создать кастомную роль."""
        handler = CreateOrgRoleHandler(
            role_repo=role_repo,
            org_permission_checker=org_permission_checker,
            event_bus=event_bus,
        )
        command = CreateOrgRoleCommand(
            caller_id=caller_id,
            org_id=org_id,
            name=body.name,
            permissions=body.permissions,
            scope=body.scope,
            description=body.description,
        )
        dto = await handler.handle(command)
        return SuccessResponse(data=OrgRoleResponse.model_validate(dto.model_dump()))

    async def update_role(
        self,
        org_id: str,
        role_id: str,
        body: UpdateOrgRoleRequest,
        caller_id: str = Depends(get_current_user_id),
        role_repo=Depends(get_org_role_repository),
        org_permission_checker=Depends(get_org_permission_checker),
        event_bus=Depends(get_organization_event_bus),
    ) -> MessageResponse:
        """Обновить роль."""
        handler = UpdateOrgRoleHandler(
            role_repo=role_repo,
            org_permission_checker=org_permission_checker,
            event_bus=event_bus,
        )
        command = UpdateOrgRoleCommand(
            caller_id=caller_id,
            org_id=org_id,
            role_id=role_id,
            permissions=body.permissions,
            description=body.description,
        )
        await handler.handle(command)
        return MessageResponse(message="Роль обновлена")

    async def delete_role(
        self,
        org_id: str,
        role_id: str,
        caller_id: str = Depends(get_current_user_id),
        role_repo=Depends(get_org_role_repository),
        org_permission_checker=Depends(get_org_permission_checker),
        event_bus=Depends(get_organization_event_bus),
    ) -> MessageResponse:
        """Удалить роль."""
        handler = DeleteOrgRoleHandler(
            role_repo=role_repo,
            org_permission_checker=org_permission_checker,
            event_bus=event_bus,
        )
        command = DeleteOrgRoleCommand(
            caller_id=caller_id,
            org_id=org_id,
            role_id=role_id,
        )
        await handler.handle(command)
        return MessageResponse(message="Роль удалена")
