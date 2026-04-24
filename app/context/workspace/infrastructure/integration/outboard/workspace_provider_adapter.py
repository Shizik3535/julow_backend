from __future__ import annotations

from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.application.dto.workspace_dto import WorkspaceDTO
from app.context.workspace.application.ports.integration.outboard.workspace_provider import WorkspaceProvider
from app.context.workspace.domain.repositories.workspace_repository import WorkspaceRepository


class WorkspaceProviderAdapter(WorkspaceProvider):
    """Реализация WorkspaceProvider (outboard) — предоставляет данные workspace другим BC."""

    def __init__(self, repo: WorkspaceRepository) -> None:
        self._repo = repo

    async def get_workspace(self, workspace_id: str) -> WorkspaceDTO | None:
        workspace = await self._repo.get_by_id(Id.from_string(workspace_id))
        if workspace is None:
            return None
        return WorkspaceDTO(
            id=str(workspace.id),
            name=workspace.name,
            status=workspace.status.value,
            workspace_type=workspace.workspace_type.value,
            organization_id=str(workspace.organization_id) if workspace.organization_id else None,
            parent_workspace_id=str(workspace.parent_workspace_id) if workspace.parent_workspace_id else None,
            owner_ids=[str(uid) for uid in workspace.owner_ids],
            created_at=workspace.created_at,
            updated_at=workspace.updated_at,
        )

    async def workspace_exists(self, workspace_id: str) -> bool:
        workspace = await self._repo.get_by_id(Id.from_string(workspace_id))
        return workspace is not None

    async def get_workspaces_by_organization(self, org_id: str) -> list[WorkspaceDTO]:
        workspaces = await self._repo.get_by_organization(Id.from_string(org_id))
        return [
            WorkspaceDTO(
                id=str(ws.id),
                name=ws.name,
                status=ws.status.value,
                workspace_type=ws.workspace_type.value,
                organization_id=str(ws.organization_id) if ws.organization_id else None,
                parent_workspace_id=str(ws.parent_workspace_id) if ws.parent_workspace_id else None,
                owner_ids=[str(uid) for uid in ws.owner_ids],
                created_at=ws.created_at,
                updated_at=ws.updated_at,
            )
            for ws in workspaces
        ]
