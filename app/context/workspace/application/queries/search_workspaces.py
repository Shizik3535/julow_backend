from __future__ import annotations

from typing import Any

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.application.dto.workspace_dto import WorkspaceDTO, WorkspaceListDTO
from app.context.workspace.application.ports.authorization.workspace_permission_checker_port import (
    WorkspacePermissionCheckerPort,
)
from app.context.workspace.domain.repositories.workspace_repository import WorkspaceRepository


class SearchWorkspacesQuery(BaseQuery):
    """
    Запрос поиска workspace с фильтрацией.

    Атрибуты:
        caller_id: ID пользователя, выполняющего запрос.
        offset: Смещение.
        limit: Лимит.
        filters: Фильтры (dict).
    """

    caller_id: str
    offset: int = 0
    limit: int = 100
    filters: dict[str, Any] | None = None


class SearchWorkspacesHandler(BaseQueryHandler[SearchWorkspacesQuery, WorkspaceListDTO]):
    """
    Обработчик поиска workspace.

    После выборки результаты фильтруются: остаются только те workspace,
    к которым у caller есть разрешение `ws.read` (включая каскад орг-роли).
    """

    REQUIRED_PERMISSION = "ws.read"

    def __init__(
        self,
        ws_repo: WorkspaceRepository,
        permission_checker: WorkspacePermissionCheckerPort,
    ) -> None:
        super().__init__()
        self._ws_repo = ws_repo
        self._permission_checker = permission_checker

    async def handle(self, query: SearchWorkspacesQuery) -> WorkspaceListDTO:
        caller_id = Id.from_string(query.caller_id)
        workspaces = await self._ws_repo.search(
            offset=query.offset,
            limit=query.limit,
            filters=query.filters,
        )
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
                    parent_workspace_id=str(ws.parent_workspace_id) if ws.parent_workspace_id else None,
                    owner_ids=[str(oid) for oid in ws.owner_ids],
                    created_at=ws.created_at,
                    updated_at=ws.updated_at,
                )
            )
        return WorkspaceListDTO(items=items, total=len(items))
