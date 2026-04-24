from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.project.domain.exceptions.project_exceptions import ProjectNotFoundException
from app.context.project.domain.repositories.project_membership_repository import ProjectMembershipRepository
from app.context.project.domain.repositories.project_repository import ProjectRepository
from app.context.project.application.ports.authorization.project_permission_checker_port import (
    ProjectPermissionCheckerPort,
)


class RemoveProjectMemberCommand(BaseCommand):
    """
    Команда удаления участника из проекта.

    Атрибуты:
        caller_id: ID пользователя, выполняющего операцию.
        project_id: ID проекта.
        user_id: ID удаляемого участника.
    """

    caller_id: str
    project_id: str
    user_id: str


class RemoveProjectMemberHandler(BaseCommandHandler[RemoveProjectMemberCommand, None]):
    """
    Обработчик удаления участника из проекта.

    Проверяет is_owner через Project AR.
    """


    REQUIRED_PERMISSION = "members.write"

    def __init__(
        self,
        project_repo: ProjectRepository,
        membership_repo: ProjectMembershipRepository,
        permission_checker: ProjectPermissionCheckerPort,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._project_repo = project_repo
        self._membership_repo = membership_repo
        self._event_bus = event_bus
        self._permission_checker = permission_checker
    async def handle(self, command: RemoveProjectMemberCommand) -> None:
        await self._permission_checker.require_permission(
            user_id=Id.from_string(command.caller_id),
            project_id=Id.from_string(command.project_id),
            permission=self.REQUIRED_PERMISSION,
        )
        project = await self._project_repo.get_by_id(Id.from_string(command.project_id))
        if project is None:
            raise ProjectNotFoundException(command.project_id)

        membership = await self._membership_repo.get_by_project_id(Id.from_string(command.project_id))
        if membership is None:
            raise ProjectNotFoundException(command.project_id)

        user_id = Id.from_string(command.user_id)
        is_owner = user_id in project.owner_ids

        membership.remove_member(user_id, is_owner=is_owner)
        await self._membership_repo.update(membership)
        await self._event_bus.publish_all(membership.clear_domain_events())
