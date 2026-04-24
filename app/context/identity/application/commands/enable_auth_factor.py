from __future__ import annotations

import secrets as _secrets

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.identity.application.dto.enable_auth_factor_result_dto import EnableAuthFactorResultDTO
from app.context.identity.application.ports.two_fa.totp_port import TOTPPort
from app.context.identity.domain.exceptions.user_exceptions import UserNotFoundException
from app.context.identity.domain.repositories.user_auth_repository import UserAuthRepository
from app.context.identity.domain.value_objects.two_fa_secret import TwoFASecret
from app.context.identity.domain.value_objects.two_factor_method import TwoFactorMethod


class EnableAuthFactorCommand(BaseCommand):
    """
    Команда включения фактора 2FA.

    Атрибуты:
        user_id: Идентификатор пользователя.
        method: Метод 2FA (totp, email_code, app).
        is_primary: Является ли основным фактором.
    """

    user_id: str
    method: str
    is_primary: bool = False


class EnableAuthFactorHandler(BaseCommandHandler[EnableAuthFactorCommand, EnableAuthFactorResultDTO]):
    """
    Обработчик включения фактора 2FA.

    Для TOTP — генерирует секрет через TOTPPort, включает фактор,
    возвращает provisioning URI для QR-кода.
    """

    def __init__(
        self,
        user_auth_repo: UserAuthRepository,
        totp_port: TOTPPort,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._user_auth_repo = user_auth_repo
        self._totp_port = totp_port
        self._event_bus = event_bus

    async def handle(self, command: EnableAuthFactorCommand) -> EnableAuthFactorResultDTO:
        user_id = Id.from_string(command.user_id)

        user_auth = await self._user_auth_repo.get_by_user_id(user_id)
        if user_auth is None:
            raise UserNotFoundException(command.user_id)

        method = TwoFactorMethod(command.method)

        provisioning_uri: str | None = None
        raw_secret: str | None = None

        if method == TwoFactorMethod.TOTP:
            raw_secret = self._totp_port.generate_secret()
            provisioning_uri = self._totp_port.get_provisioning_uri(
                secret=raw_secret,
                email=user_auth.email.value,
                issuer="Julow",
            )
        else:
            raw_secret = _secrets.token_urlsafe(32)

        secret = TwoFASecret(value=raw_secret, method=method)

        user_auth.enable_auth_factor(
            method=method,
            secret=secret,
            is_primary=command.is_primary,
        )

        await self._user_auth_repo.update(user_auth)
        await self._event_bus.publish_all(user_auth.clear_domain_events())

        return EnableAuthFactorResultDTO(
            method=method.value,
            provisioning_uri=provisioning_uri,
            secret=raw_secret,
        )
