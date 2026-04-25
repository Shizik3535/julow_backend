from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.application.ports.authorization.org_permission_checker_port import OrgPermissionCheckerPort
from app.context.organization.application.exceptions.membership_app_exceptions import MemberNotInOrganizationException
from app.shared.domain.exceptions import EntityNotFoundException
from app.context.organization.domain.repositories.department_repository import DepartmentRepository
from app.context.organization.domain.repositories.org_membership_repository import OrgMembershipRepository


class AddDepartmentMemberCommand(BaseCommand):
    """
    Команда добавления участника в подразделение.

    Атрибуты:
        department_id: ID подразделения.
        user_id: ID пользователя.
    """

    caller_id: str
    org_id: str
    department_id: str
    user_id: str


class AddDepartmentMemberHandler(BaseCommandHandler[AddDepartmentMemberCommand, None]):
    """
    Обработчик добавления участника в подразделение.

    ACL: проверяет, что пользователь является членом организации,
    затем добавляет в Department.
    """

    REQUIRED_PERMISSION = "departments.write"

    def __init__(
        self,
        department_repo: DepartmentRepository,
        membership_repo: OrgMembershipRepository,
        org_permission_checker: OrgPermissionCheckerPort,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._department_repo = department_repo
        self._membership_repo = membership_repo
        self._org_permission_checker = org_permission_checker
        self._event_bus = event_bus

    async def handle(self, command: AddDepartmentMemberCommand) -> None:
        caller_id = Id.from_string(command.caller_id)
        org_id = Id.from_string(command.org_id)

        department = await self._department_repo.get_by_id(Id.from_string(command.department_id))
        if department is None:
            raise EntityNotFoundException(entity_type="Department", id=command.department_id)
        await self._org_permission_checker.require_permission(caller_id, org_id, self.REQUIRED_PERMISSION)
        user_id = Id.from_string(command.user_id)

        member = await self._membership_repo.get_member_by_org_and_user(department.org_id, user_id)
        if member is None:
            raise MemberNotInOrganizationException(command.user_id, str(department.org_id))

        department.add_member(user_id)
        await self._department_repo.update(department)
        await self._event_bus.publish_all(department.clear_domain_events())
