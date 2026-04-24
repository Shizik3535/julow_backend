from __future__ import annotations

import logging

from app.shared.application.base_event_handler import BaseEventHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.project.domain.repositories.project_membership_repository import ProjectMembershipRepository
from app.context.project.domain.repositories.project_repository import ProjectRepository
from app.context.workspace.domain.events.workspace_membership_events import WorkspaceMemberRemoved

logger = logging.getLogger(__name__)


class OnWorkspaceMemberRemoved(BaseEventHandler[WorkspaceMemberRemoved]):
    """
    Cross-BC event handler.

    Подписка на workspace.events → WorkspaceMemberRemoved.
    Удаляет участника из всех проектов этого workspace.
    """

    def __init__(
        self,
        project_repo: ProjectRepository,
        membership_repo: ProjectMembershipRepository,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._project_repo = project_repo
        self._membership_repo = membership_repo
        self._event_bus = event_bus

    async def handle(self, event: WorkspaceMemberRemoved) -> None:
        workspace_id = Id.from_string(event.workspace_id)
        user_id = Id.from_string(event.user_id)

        projects = await self._project_repo.get_by_workspace(workspace_id)
        for project in projects:
            membership = await self._membership_repo.get_by_project_id(project.id)
            if membership is None:
                continue

            member = membership._find_member(user_id)
            if member is None:
                continue

            is_owner = user_id in project.owner_ids
            if is_owner:
                logger.warning(
                    "Пропуск удаления владельца %s из проекта %s при удалении из workspace %s",
                    event.user_id,
                    str(project.id),
                    event.workspace_id,
                )
                continue

            membership.remove_member(user_id, is_owner=False)
            await self._membership_repo.update(membership)
            await self._event_bus.publish_all(membership.clear_domain_events())
            logger.info(
                "Участник %s удалён из проекта %s (workspace %s)",
                event.user_id,
                str(project.id),
                event.workspace_id,
            )
