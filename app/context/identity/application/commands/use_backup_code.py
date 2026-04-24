from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.ports.auth.password_port import PasswordPort
from app.shared.domain.value_objects.id_vo import Id
from app.context.identity.domain.exceptions.user_exceptions import UserNotFoundException
from app.context.identity.domain.repositories.user_auth_repository import UserAuthRepository


class UseBackupCodeCommand(BaseCommand):
    """
    Команда использования резервного кода 2FA.

    Атрибуты:
        user_id: Идентификатор пользователя.
        code: Резервный код в открытом виде.
    """

    user_id: str
    code: str


class UseBackupCodeHandler(BaseCommandHandler[UseBackupCodeCommand, None]):
    """
    Обработчик использования резервного кода.

    Проверяет код через verify_password и помечает как использованный.
    """

    def __init__(
        self,
        user_auth_repo: UserAuthRepository,
        password_port: PasswordPort,
    ) -> None:
        super().__init__()
        self._user_auth_repo = user_auth_repo
        self._password_port = password_port

    async def handle(self, command: UseBackupCodeCommand) -> None:
        user_id = Id.from_string(command.user_id)

        user_auth = await self._user_auth_repo.get_by_user_id(user_id)
        if user_auth is None:
            raise UserNotFoundException(command.user_id)

        user_auth.use_backup_code(command.code, self._password_port.verify_password)

        await self._user_auth_repo.update(user_auth)
