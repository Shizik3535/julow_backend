from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.application.ports.authorization.org_permission_checker_port import OrgPermissionCheckerPort
from app.context.organization.application.exceptions.membership_app_exceptions import MemberNotInOrganizationException
from app.context.organization.domain.exceptions.team_exceptions import TeamNotFoundException
from app.context.organization.domain.repositories.org_membership_repository import OrgMembershipRepository
from app.context.organization.domain.repositories.team_repository import TeamRepository


class AddTeamMemberCommand(BaseCommand):
    """
    Команда добавления участника в команду.

    Атрибуты:
        team_id: ID команды.
        user_id: ID пользователя.
    """

    caller_id: str
    org_id: str
    team_id: str
    user_id: str


class AddTeamMemberHandler(BaseCommandHandler[AddTeamMemberCommand, None]):
    """
    Обработчик добавления участника в команду.

    ACL: проверяет, что пользователь является членом организации,
    затем добавляет в Team.
    """

    REQUIRED_PERMISSION = "teams.write"

    def __init__(
        self,
        team_repo: TeamRepository,
        membership_repo: OrgMembershipRepository,
        org_permission_checker: OrgPermissionCheckerPort,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._team_repo = team_repo
        self._membership_repo = membership_repo
        self._org_permission_checker = org_permission_checker
        self._event_bus = event_bus

    async def handle(self, command: AddTeamMemberCommand) -> None:
        caller_id = Id.from_string(command.caller_id)
        org_id = Id.from_string(command.org_id)

        team = await self._team_repo.get_by_id(Id.from_string(command.team_id))
        if team is None:
            raise TeamNotFoundException(command.team_id)
        await self._org_permission_checker.require_permission(caller_id, org_id, self.REQUIRED_PERMISSION)
        user_id = Id.from_string(command.user_id)

        member = await self._membership_repo.get_member_by_org_and_user(team.org_id, user_id)
        if member is None:
            raise MemberNotInOrganizationException(command.user_id, str(team.org_id))

        team.add_member(user_id)
        await self._team_repo.update(team)
        await self._event_bus.publish_all(team.clear_domain_events())
