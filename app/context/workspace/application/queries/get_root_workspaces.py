from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.application.dto.workspace_dto import WorkspaceDTO, WorkspaceListDTO
from app.context.workspace.application.ports.authorization.workspace_permission_checker_port import (
    WorkspacePermissionCheckerPort,
)
from app.context.workspace.domain.repositories.workspace_repository import WorkspaceRepository


class GetRootWorkspacesQuery(BaseQuery):
    """Запрос корневых workspace (без родителя)."""

    caller_id: str


class GetRootWorkspacesHandler(BaseQueryHandler[GetRootWorkspacesQuery, WorkspaceListDTO]):
    """Обработчик запроса корневых workspace."""

    REQUIRED_PERMISSION = "ws.read"

    def __init__(self, ws_repo: WorkspaceRepository, permission_checker: WorkspacePermissionCheckerPort) -> None:
        super().__init__()
        self._ws_repo = ws_repo
        self._permission_checker = permission_checker

    async def handle(self, query: GetRootWorkspacesQuery) -> WorkspaceListDTO:
        workspaces = await self._ws_repo.get_root_workspaces()
        caller_id = Id.from_string(query.caller_id)
        items: list[WorkspaceDTO] = []
        for ws in workspaces:
            allowed = await self._permission_checker.has_permission(
                user_id=caller_id,
                workspace_id=ws.id,
                permission=self.REQUIRED_PERMISSION,
            )
            if not allowed:
                continue
            items.append(
                WorkspaceDTO(
                    id=str(ws.id),
                    name=ws.name,
                    status=ws.status.value,
                    workspace_type=ws.workspace_type.value,
                    organization_id=str(ws.organization_id) if ws.organization_id else None,
                    parent_workspace_id=None,
                    owner_ids=[str(oid) for oid in ws.owner_ids],
                    created_at=ws.created_at,
                    updated_at=ws.updated_at,
                )
            )
        return WorkspaceListDTO(items=items, total=len(items))
