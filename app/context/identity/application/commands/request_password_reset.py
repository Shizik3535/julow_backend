from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.email_vo import Email
from app.context.identity.application.ports.notification.identity_notification_port import IdentityNotificationPort
from app.context.identity.domain.repositories.user_auth_repository import UserAuthRepository
from app.context.identity.domain.value_objects.verification_token import VerificationToken
from app.context.identity.domain.value_objects.verification_type import VerificationType


class RequestPasswordResetCommand(BaseCommand):
    """
    Команда запроса сброса пароля.

    Атрибуты:
        email: Email-адрес пользователя.
    """

    email: str


class RequestPasswordResetHandler(BaseCommandHandler[RequestPasswordResetCommand, None]):
    """
    Обработчик запроса сброса пароля.

    Находит UserAuth по email и создаёт токен сброса пароля.
    Если пользователь не найден — тихо игнорирует (security best practice).
    """

    RESET_TOKEN_TTL_HOURS: int = 1

    def __init__(
        self,
        user_auth_repo: UserAuthRepository,
        event_bus: DomainEventBus,
        notification_port: IdentityNotificationPort,
    ) -> None:
        super().__init__()
        self._user_auth_repo = user_auth_repo
        self._event_bus = event_bus
        self._notification_port = notification_port

    async def handle(self, command: RequestPasswordResetCommand) -> None:
        email = Email(command.email)

        user_auth = await self._user_auth_repo.get_by_email(email)
        if user_auth is None:
            return

        token_value = str(uuid.uuid4())
        expires_at = datetime.now(tz=timezone.utc) + timedelta(hours=self.RESET_TOKEN_TTL_HOURS)

        token = VerificationToken(
            value=token_value,
            token_type=VerificationType.PASSWORD_RESET,
            expires_at=expires_at,
        )

        user_auth.request_password_reset(token=token, expires_at=expires_at)
        await self._user_auth_repo.update(user_auth)

        await self._event_bus.publish_all(user_auth.clear_domain_events())

        await self._notification_port.send_password_reset(
            email=command.email,
            token=token_value,
        )
