from __future__ import annotations

from app.context.project.application.ports.integration.outboard.project_membership_provider import (
    ProjectMembershipProvider,
)
from app.context.task.application.ports.integration.inboard.project_membership_port import (
    ProjectMembershipPort,
)


class ProjectMembershipAdapter(ProjectMembershipPort):
    """
    Реализация inboard-порта ProjectMembershipPort для Task BC.

    Делегирует проверку участия в проекте в outboard-порт
    Project BC (ProjectMembershipProvider).
    """

    def __init__(self, project_membership_provider: ProjectMembershipProvider) -> None:
        self._provider = project_membership_provider

    async def is_project_member(self, project_id: str, user_id: str) -> bool:
        return await self._provider.is_project_member(project_id=project_id, user_id=user_id)
