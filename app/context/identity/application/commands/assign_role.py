from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.identity.application.ports.authorization.permission_checker_port import PermissionCheckerPort
from app.context.identity.domain.repositories.role_repository import RoleRepository
from app.context.identity.domain.repositories.user_repository import UserRepository
from app.context.identity.domain.exceptions.user_exceptions import RoleNotFoundException, UserNotFoundException


class AssignRoleCommand(BaseCommand):
    """
    Команда назначения роли пользователю.

    Атрибуты:
        caller_id: Идентификатор пользователя, выполняющего операцию.
        user_id: Идентификатор пользователя, которому назначается роль.
        role_id: Идентификатор назначаемой роли.
    """

    caller_id: str
    user_id: str
    role_id: str


class AssignRoleHandler(BaseCommandHandler[AssignRoleCommand, None]):
    """
    Обработчик назначения роли.

    Проверяет разрешение caller'а, загружает User и Role,
    назначает роль, сохраняет.
    """

    REQUIRED_PERMISSION = "users.write"

    def __init__(
        self,
        user_repo: UserRepository,
        role_repo: RoleRepository,
        event_bus: DomainEventBus,
        permission_checker: PermissionCheckerPort,
    ) -> None:
        super().__init__()
        self._user_repo = user_repo
        self._role_repo = role_repo
        self._event_bus = event_bus
        self._permission_checker = permission_checker

    async def handle(self, command: AssignRoleCommand) -> None:
        caller_id = Id.from_string(command.caller_id)
        await self._permission_checker.require_permission(caller_id, self.REQUIRED_PERMISSION)

        user_id = Id.from_string(command.user_id)
        role_id = Id.from_string(command.role_id)

        role = await self._role_repo.get_by_id(role_id)
        if role is None:
            raise RoleNotFoundException(command.role_id)

        user = await self._user_repo.get_by_id(user_id)
        if user is None:
            raise UserNotFoundException(command.user_id)

        user.assign_role(role_id)

        await self._user_repo.update(user)
        await self._event_bus.publish_all(user.clear_domain_events())
