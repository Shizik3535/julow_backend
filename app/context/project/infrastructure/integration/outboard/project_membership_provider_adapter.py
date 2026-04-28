from __future__ import annotations

from app.context.project.application.dto.project_member_dto import ProjectMemberDTO
from app.context.project.application.ports.integration.outboard.project_membership_provider import (
    ProjectMembershipProvider,
)
from app.context.project.domain.repositories.project_membership_repository import (
    ProjectMembershipRepository,
)
from app.shared.domain.value_objects.id_vo import Id


class ProjectMembershipProviderAdapter(ProjectMembershipProvider):
    """
    Реализация outboard-порта ProjectMembershipProvider.

    Делегирует в ProjectMembershipRepository для предоставления
    данных участников проекта другим BC.
    """

    def __init__(self, repo: ProjectMembershipRepository) -> None:
        self._repo = repo

    async def is_project_member(self, project_id: str, user_id: str) -> bool:
        member = await self._repo.get_member_by_project_and_user(
            Id.from_string(project_id), Id.from_string(user_id),
        )
        return member is not None and member.is_active

    async def get_member(self, project_id: str, user_id: str) -> ProjectMemberDTO | None:
        member = await self._repo.get_member_by_project_and_user(
            Id.from_string(project_id), Id.from_string(user_id),
        )
        if member is None:
            return None
        return ProjectMemberDTO(
            id=str(member.id),
            user_id=str(member.user_id),
            role_id=str(member.role_id),
            joined_at=member.joined_at,
            is_active=member.is_active,
        )

    async def get_member_role(self, project_id: str, user_id: str) -> str | None:
        member = await self._repo.get_member_by_project_and_user(
            Id.from_string(project_id), Id.from_string(user_id),
        )
        if member is None:
            return None
        return str(member.role_id)

    async def get_project_member_ids(self, project_id: str) -> list[str]:
        memberships = await self._repo.get_members_by_project(Id.from_string(project_id))
        return [str(m.user_id) for m in memberships if m.is_active]
