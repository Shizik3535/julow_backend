from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.application.dto.workspace_dto import WorkspaceDTO, WorkspaceListDTO
from app.context.workspace.domain.repositories.workspace_repository import WorkspaceRepository


class GetWorkspacesByOwnerQuery(BaseQuery):
    """
    Запрос workspace по ID владельца.

    Атрибуты:
        owner_id: ID владельца.
    """

    owner_id: str


class GetWorkspacesByOwnerHandler(BaseQueryHandler[GetWorkspacesByOwnerQuery, WorkspaceListDTO]):
    """Обработчик запроса workspace по владельцу."""

    def __init__(self, ws_repo: WorkspaceRepository) -> None:
        super().__init__()
        self._ws_repo = ws_repo

    async def handle(self, query: GetWorkspacesByOwnerQuery) -> WorkspaceListDTO:
        workspaces = await self._ws_repo.get_by_owner(Id.from_string(query.owner_id))
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
