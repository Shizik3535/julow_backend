from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.application.ports.auth.password_port import PasswordPort
from app.shared.domain.value_objects.email_vo import Email
from app.context.identity.domain.repositories.user_auth_repository import UserAuthRepository
from app.context.identity.domain.value_objects.password_hash import PasswordHash


class ResetPasswordCommand(BaseCommand):
    """
    Команда сброса пароля по токену.

    Атрибуты:
        email: Email-адрес пользователя.
        token: Токен сброса пароля.
        new_password: Новый пароль в открытом виде.
    """

    email: str
    token: str
    new_password: str


class ResetPasswordHandler(BaseCommandHandler[ResetPasswordCommand, None]):
    """
    Обработчик сброса пароля.

    Находит UserAuth по email, сбрасывает пароль по токену.
    """

    def __init__(
        self,
        user_auth_repo: UserAuthRepository,
        password_port: PasswordPort,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._user_auth_repo = user_auth_repo
        self._password_port = password_port
        self._event_bus = event_bus

    async def handle(self, command: ResetPasswordCommand) -> None:
        email = Email(command.email)

        user_auth = await self._user_auth_repo.get_by_email(email)
        if user_auth is None:
            from app.context.identity.domain.exceptions.user_exceptions import UserNotFoundException
            raise UserNotFoundException(command.email)

        hashed = self._password_port.hash_password(command.new_password)
        user_auth.reset_password(
            token_value=command.token,
            new_password_hash=PasswordHash(value=hashed),
        )

        await self._user_auth_repo.update(user_auth)

        await self._event_bus.publish_all(user_auth.clear_domain_events())
