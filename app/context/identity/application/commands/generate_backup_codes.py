from __future__ import annotations

import secrets
import string

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.ports.auth.password_port import PasswordPort
from app.shared.domain.value_objects.id_vo import Id
from app.context.identity.application.dto.backup_codes_result_dto import BackupCodesResultDTO
from app.context.identity.domain.exceptions.user_exceptions import UserNotFoundException
from app.context.identity.domain.repositories.user_auth_repository import UserAuthRepository


class GenerateBackupCodesCommand(BaseCommand):
    """
    Команда генерации резервных кодов 2FA.

    Атрибуты:
        user_id: Идентификатор пользователя.
        count: Количество кодов для генерации.
    """

    user_id: str
    count: int = 10


class GenerateBackupCodesHandler(BaseCommandHandler[GenerateBackupCodesCommand, BackupCodesResultDTO]):
    """
    Обработчик генерации резервных кодов.

    Генерирует plain-коды, хеширует, передаёт в агрегат.
    Возвращает plain-коды один раз — они не хранятся.
    """

    CODE_LENGTH: int = 8
    CODE_ALPHABET: str = string.ascii_uppercase + string.digits

    def __init__(
        self,
        user_auth_repo: UserAuthRepository,
        password_port: PasswordPort,
    ) -> None:
        super().__init__()
        self._user_auth_repo = user_auth_repo
        self._password_port = password_port

    async def handle(self, command: GenerateBackupCodesCommand) -> BackupCodesResultDTO:
        user_id = Id.from_string(command.user_id)

        user_auth = await self._user_auth_repo.get_by_user_id(user_id)
        if user_auth is None:
            raise UserNotFoundException(command.user_id)

        plain_codes: list[str] = []
        code_hashes: list[str] = []
        for _ in range(command.count):
            code = "".join(secrets.choice(self.CODE_ALPHABET) for _ in range(self.CODE_LENGTH))
            plain_codes.append(code)
            code_hashes.append(self._password_port.hash_password(code))

        user_auth.generate_backup_codes(code_hashes)

        await self._user_auth_repo.update(user_auth)

        return BackupCodesResultDTO(codes=plain_codes)
