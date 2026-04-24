from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.domain.value_objects.id_vo import Id
from app.context.identity.application.ports.authorization.permission_checker_port import PermissionCheckerPort
from app.context.identity.domain.exceptions.user_exceptions import UserNotFoundException
from app.context.identity.domain.repositories.user_auth_repository import UserAuthRepository


class UnlockAccountCommand(BaseCommand):
    """
    Команда разблокировки аккаунта (административная).

    Атрибуты:
        caller_id: Идентификатор пользователя, выполняющего операцию.
        user_id: Идентификатор пользователя для разблокировки.
    """

    caller_id: str
    user_id: str


class UnlockAccountHandler(BaseCommandHandler[UnlockAccountCommand, None]):
    """
    Обработчик разблокировки аккаунта.

    Проверяет разрешение caller'а, загружает UserAuth,
    сбрасывает блокировку, сохраняет.
    """

    REQUIRED_PERMISSION = "users.support"

    def __init__(
        self,
        user_auth_repo: UserAuthRepository,
        permission_checker: PermissionCheckerPort,
    ) -> None:
        super().__init__()
        self._user_auth_repo = user_auth_repo
        self._permission_checker = permission_checker

    async def handle(self, command: UnlockAccountCommand) -> None:
        caller_id = Id.from_string(command.caller_id)
        await self._permission_checker.require_permission(caller_id, self.REQUIRED_PERMISSION)

        user_id = Id.from_string(command.user_id)

        user_auth = await self._user_auth_repo.get_by_user_id(user_id)
        if user_auth is None:
            raise UserNotFoundException(command.user_id)

        user_auth.unlock()

        await self._user_auth_repo.update(user_auth)
