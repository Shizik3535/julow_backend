from __future__ import annotations

from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.application.dto.workspace_member_dto import WorkspaceMemberDTO
from app.context.workspace.application.ports.integration.outboard.workspace_membership_provider import (
    WorkspaceMembershipProvider,
)
from app.context.workspace.domain.repositories.workspace_membership_repository import WorkspaceMembershipRepository
from app.context.workspace.domain.repositories.workspace_repository import WorkspaceRepository
from app.context.workspace.domain.repositories.workspace_role_repository import WorkspaceRoleRepository


class WorkspaceMembershipProviderAdapter(WorkspaceMembershipProvider):
    """
    Реализация WorkspaceMembershipProvider (outboard) — предоставляет
    данные о членстве и разрешениях workspace другим BC.
    """

    def __init__(
        self,
        membership_repo: WorkspaceMembershipRepository,
        workspace_role_repo: WorkspaceRoleRepository,
        workspace_repo: WorkspaceRepository,
    ) -> None:
        self._membership_repo = membership_repo
        self._workspace_role_repo = workspace_role_repo
        self._workspace_repo = workspace_repo

    async def is_member(self, workspace_id: str, user_id: str) -> bool:
        member = await self._membership_repo.get_member_by_workspace_and_user(
            workspace_id=Id.from_string(workspace_id),
            user_id=Id.from_string(user_id),
        )
        return member is not None and member.is_active

    async def get_member_role(self, workspace_id: str, user_id: str) -> str | None:
        member = await self._membership_repo.get_member_by_workspace_and_user(
            workspace_id=Id.from_string(workspace_id),
            user_id=Id.from_string(user_id),
        )
        if member is None:
            return None
        return str(member.role_id)

    async def get_members(self, workspace_id: str) -> list[WorkspaceMemberDTO]:
        members = await self._membership_repo.get_members_by_workspace(
            workspace_id=Id.from_string(workspace_id),
        )
        return [
            WorkspaceMemberDTO(
                id=str(m.id),
                user_id=str(m.user_id),
                display_name=m.display_name,
                role_id=str(m.role_id),
                joined_at=m.joined_at,
                is_active=m.is_active,
                source=m.source.value,
                invited_by=str(m.invited_by) if m.invited_by else None,
            )
            for m in members
        ]

    async def has_permission(self, workspace_id: str, user_id: str, permission: str) -> bool:
        # 1. Проверка через workspace-роль
        member = await self._membership_repo.get_member_by_workspace_and_user(
            workspace_id=Id.from_string(workspace_id),
            user_id=Id.from_string(user_id),
        )
        if member is not None and member.is_active:
            role = await self._workspace_role_repo.get_by_id(member.role_id)
            if role is not None and self._permission_grants(role.permissions, permission):
                return True

        # 2. Каскад: проверка через орг-роль (если workspace привязан к организации)
        workspace = await self._workspace_repo.get_by_id(Id.from_string(workspace_id))
        if workspace is None or workspace.organization_id is None:
            return False

        # Орг-проверка делегируется потребителю через OrganizationPermissionCheckerPort
        return False

    @staticmethod
    def _permission_grants(permissions: list[str], required: str) -> bool:
        for perm in permissions:
            if perm == required:
                return True
            if perm.endswith(".*"):
                prefix = perm[:-1]
                if required.startswith(prefix):
                    return True
        return False
