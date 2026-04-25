from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.application.dto.workspace_dto import WorkspaceDTO, WorkspaceListDTO
from app.context.workspace.application.ports.authorization.workspace_permission_checker_port import (
    WorkspacePermissionCheckerPort,
)
from app.context.workspace.domain.exceptions.workspace_exceptions import WorkspaceNotFoundException
from app.context.workspace.domain.repositories.workspace_repository import WorkspaceRepository


class GetChildWorkspacesQuery(BaseQuery):
    """
    Запрос дочерних workspace.

    Атрибуты:
        caller_id: ID пользователя, выполняющего запрос.
        parent_workspace_id: ID родительского workspace.
    """

    caller_id: str
    parent_workspace_id: str


class GetChildWorkspacesHandler(BaseQueryHandler[GetChildWorkspacesQuery, WorkspaceListDTO]):
    """Обработчик запроса дочерних workspace."""

    REQUIRED_PERMISSION = "ws.read"

    def __init__(
        self,
        ws_repo: WorkspaceRepository,
        permission_checker: WorkspacePermissionCheckerPort,
    ) -> None:
        super().__init__()
        self._ws_repo = ws_repo
        self._permission_checker = permission_checker

    async def handle(self, query: GetChildWorkspacesQuery) -> WorkspaceListDTO:
        parent_id = Id.from_string(query.parent_workspace_id)

        parent = await self._ws_repo.get_by_id(parent_id)
        if parent is None:
            raise WorkspaceNotFoundException(query.parent_workspace_id)
        await self._permission_checker.require_permission(
            user_id=Id.from_string(query.caller_id),
            workspace_id=parent_id,
            permission=self.REQUIRED_PERMISSION,
        )
        children = await self._ws_repo.get_children(parent_id)
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
            for ws in children
        ]
        return WorkspaceListDTO(items=items, total=len(items))
