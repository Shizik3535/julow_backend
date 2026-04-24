from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.application.ports.auth.password_port import PasswordPort
from app.shared.domain.value_objects.id_vo import Id
from app.context.identity.application.exceptions.auth_app_exceptions import AuthenticationFailedException
from app.context.identity.application.ports.notification.identity_notification_port import IdentityNotificationPort
from app.context.identity.domain.exceptions.user_exceptions import UserNotFoundException
from app.context.identity.domain.repositories.user_auth_repository import UserAuthRepository
from app.context.identity.domain.value_objects.password_hash import PasswordHash


class ChangePasswordCommand(BaseCommand):
    """
    Команда смены пароля.

    Атрибуты:
        user_id: Идентификатор пользователя.
        current_password: Текущий пароль в открытом виде.
        new_password: Новый пароль в открытом виде.
    """

    user_id: str
    current_password: str
    new_password: str


class ChangePasswordHandler(BaseCommandHandler[ChangePasswordCommand, None]):
    """
    Обработчик смены пароля.

    Проверяет текущий пароль, хеширует новый, вызывает доменный метод.
    """

    def __init__(
        self,
        user_auth_repo: UserAuthRepository,
        password_port: PasswordPort,
        event_bus: DomainEventBus,
        notification_port: IdentityNotificationPort,
    ) -> None:
        super().__init__()
        self._user_auth_repo = user_auth_repo
        self._password_port = password_port
        self._event_bus = event_bus
        self._notification_port = notification_port

    async def handle(self, command: ChangePasswordCommand) -> None:
        user_id = Id.from_string(command.user_id)

        user_auth = await self._user_auth_repo.get_by_user_id(user_id)
        if user_auth is None:
            raise UserNotFoundException(command.user_id)

        if user_auth.password_hash is None:
            raise AuthenticationFailedException()

        is_valid = self._password_port.verify_password(
            command.current_password, user_auth.password_hash.value
        )
        if not is_valid:
            raise AuthenticationFailedException()

        hashed = self._password_port.hash_password(command.new_password)
        user_auth.change_password(PasswordHash(value=hashed))

        await self._user_auth_repo.update(user_auth)
        await self._event_bus.publish_all(user_auth.clear_domain_events())

        await self._notification_port.send_password_changed_notification(
            email=user_auth.email.value,
        )
