from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.application.dto.workspace_dto import WorkspaceDTO, WorkspaceListDTO
from app.context.workspace.application.exceptions.authorization_exceptions import (
    InsufficientWorkspacePermissionsException,
)
from app.context.workspace.application.exceptions.organization_app_exceptions import (
    OrganizationNotFoundException,
)
from app.context.workspace.application.ports.integration.inboard.organization_membership_port import (
    OrganizationMembershipPort,
)
from app.context.workspace.application.ports.integration.inboard.organization_permission_checker_port import (
    OrganizationPermissionCheckerPort,
)
from app.context.workspace.domain.repositories.workspace_repository import WorkspaceRepository


class GetWorkspacesByOrganizationQuery(BaseQuery):
    """
    Запрос workspace по ID организации.

    Атрибуты:
        caller_id: ID пользователя, выполняющего запрос.
        organization_id: ID организации.
    """

    caller_id: str
    organization_id: str


class GetWorkspacesByOrganizationHandler(BaseQueryHandler[GetWorkspacesByOrganizationQuery, WorkspaceListDTO]):
    """
    Обработчик запроса workspace по организации.

    Кросс-BC авторизация:
        1. Caller должен быть членом организации, иначе 403.
        2. Если у caller есть орг-разрешение `workspaces.read` — возвращаются
           все workspace организации.
        3. Иначе — только те workspace, где caller является участником.
    """

    REQUIRED_ORG_PERMISSION = "workspaces.read"

    def __init__(
        self,
        ws_repo: WorkspaceRepository,
        org_membership_port: OrganizationMembershipPort,
        org_permission_checker: OrganizationPermissionCheckerPort,
    ) -> None:
        super().__init__()
        self._ws_repo = ws_repo
        self._org_membership_port = org_membership_port
        self._org_permission_checker = org_permission_checker

    async def handle(self, query: GetWorkspacesByOrganizationQuery) -> WorkspaceListDTO:
        org_id_str = query.organization_id
        caller_id_str = query.caller_id

        # 0. Проверка существования организации.
        if not await self._org_membership_port.org_exists(org_id_str):
            raise OrganizationNotFoundException(org_id_str)

        # 1. Проверка членства в организации.
        is_member = await self._org_membership_port.is_org_member(
            org_id=org_id_str, user_id=caller_id_str
        )
        if not is_member:
            raise InsufficientWorkspacePermissionsException(
                permission=self.REQUIRED_ORG_PERMISSION,
                workspace_id=org_id_str,
            )

        # 2. Проверка орг-разрешения на полное чтение workspace организации.
        can_read_all = await self._org_permission_checker.has_permission(
            user_id=caller_id_str,
            org_id=org_id_str,
            permission=self.REQUIRED_ORG_PERMISSION,
        )

        org_id = Id.from_string(org_id_str)
        if can_read_all:
            workspaces = await self._ws_repo.get_by_organization(org_id)
        else:
            # 3. Только те workspace, где caller является участником.
            workspaces = await self._ws_repo.get_by_organization_and_member(
                organization_id=org_id,
                user_id=Id.from_string(caller_id_str),
            )

        items = [
            WorkspaceDTO(
                id=str(ws.id),
                name=ws.name,
                status=ws.status.value,
                workspace_type=ws.workspace_type.value,
                organization_id=str(ws.organization_id) if ws.organization_id else None,
                parent_workspace_id=str(ws.parent_workspace_id) if ws.parent_workspace_id else None,
                owner_ids=[str(oid) for oid in ws.owner_ids],
                created_at=ws.created_at,
                updated_at=ws.updated_at,
            )
            for ws in workspaces
        ]
        return WorkspaceListDTO(items=items, total=len(items))
