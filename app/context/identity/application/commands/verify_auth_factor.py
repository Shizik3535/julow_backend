from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.domain.value_objects.id_vo import Id
from app.context.identity.application.ports.two_fa.totp_port import TOTPPort
from app.context.identity.domain.exceptions.auth_exceptions import InvalidTwoFACodeException
from app.context.identity.domain.exceptions.user_exceptions import UserNotFoundException
from app.context.identity.domain.repositories.user_auth_repository import UserAuthRepository
from app.context.identity.domain.value_objects.two_factor_method import TwoFactorMethod


class VerifyAuthFactorCommand(BaseCommand):
    """
    Команда проверки кода 2FA.

    Атрибуты:
        user_id: Идентификатор пользователя.
        method: Метод 2FA (totp, email_code, app).
        code: Код подтверждения.
    """

    user_id: str
    method: str
    code: str


class VerifyAuthFactorHandler(BaseCommandHandler[VerifyAuthFactorCommand, bool]):
    """
    Обработчик проверки кода 2FA.

    Проверяет код через TOTPPort (для TOTP), затем обновляет
    доменный агрегат. Возвращает True при успешной верификации.
    """

    def __init__(
        self,
        user_auth_repo: UserAuthRepository,
        totp_port: TOTPPort,
    ) -> None:
        super().__init__()
        self._user_auth_repo = user_auth_repo
        self._totp_port = totp_port

    async def handle(self, command: VerifyAuthFactorCommand) -> bool:
        user_id = Id.from_string(command.user_id)

        user_auth = await self._user_auth_repo.get_by_user_id(user_id)
        if user_auth is None:
            raise UserNotFoundException(command.user_id)

        method = TwoFactorMethod(command.method)

        factor = user_auth._find_auth_factor(method)
        if factor is None or not factor.is_enabled or factor.secret is None:
            raise InvalidTwoFACodeException()

        if method == TwoFactorMethod.TOTP:
            is_valid = self._totp_port.verify_code(factor.secret.value, command.code)
            if not is_valid:
                raise InvalidTwoFACodeException()

        user_auth.verify_auth_factor(method, command.code)

        await self._user_auth_repo.update(user_auth)
        return True
