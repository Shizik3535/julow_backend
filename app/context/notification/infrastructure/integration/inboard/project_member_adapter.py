from __future__ import annotations

from app.context.project.application.ports.integration.outboard.project_membership_provider import (
    ProjectMembershipProvider,
)
from app.context.project.application.ports.integration.outboard.project_provider import (
    ProjectProvider,
)
from app.context.notification.application.ports.integration.inboard.project_member_port import (
    ProjectMemberPort,
)


class ProjectMemberAdapter(ProjectMemberPort):
    """
    Реализация inboard-порта ProjectMemberPort для Notification BC.

    Делегирует получение участников проекта в outboard-порты
    Project BC (ProjectMembershipProvider + ProjectProvider для owner_ids).
    """

    def __init__(
        self,
        project_membership_provider: ProjectMembershipProvider,
        project_provider: ProjectProvider,
    ) -> None:
        self._membership_provider = project_membership_provider
        self._project_provider = project_provider

    async def get_project_members(self, project_id: str) -> list[str]:
        member_ids = await self._membership_provider.get_project_member_ids(project_id)

        # Добавляем владельцев проекта
        project_dto = await self._project_provider.get_project(project_id)
        if project_dto is not None:
            for owner_id in project_dto.owner_ids:
                if owner_id not in member_ids:
                    member_ids.append(owner_id)

        return member_ids
