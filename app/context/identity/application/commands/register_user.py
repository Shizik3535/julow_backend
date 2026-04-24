from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.application.ports.auth.password_port import PasswordPort
from app.shared.domain.value_objects.email_vo import Email
from app.context.identity.application.dto.user_dto import UserDTO
from app.context.identity.application.exceptions.user_app_exceptions import UserAlreadyExistsException
from app.context.identity.application.ports.notification.identity_notification_port import IdentityNotificationPort
from app.context.identity.domain.aggregates.user import User
from app.context.identity.domain.aggregates.user_auth import UserAuth
from app.context.identity.domain.repositories.role_repository import RoleRepository
from app.context.identity.domain.repositories.user_auth_repository import UserAuthRepository
from app.context.identity.domain.repositories.user_repository import UserRepository
from app.context.identity.domain.value_objects.auth_provider import AuthProvider
from app.context.identity.domain.value_objects.password_hash import PasswordHash
from app.context.identity.domain.value_objects.verification_token import VerificationToken
from app.context.identity.domain.value_objects.verification_type import VerificationType


class RegisterUserCommand(BaseCommand):
    """
    Команда регистрации пользователя.

    Атрибуты:
        email: Email-адрес.
        password: Пароль в открытом виде.
        auth_provider: Способ регистрации.
    """

    email: str
    password: str
    auth_provider: str = "email_password"


class RegisterUserHandler(BaseCommandHandler[RegisterUserCommand, UserDTO]):
    """
    Обработчик регистрации пользователя.

    Создаёт User + UserAuth, назначает системную роль «user»,
    запрашивает верификацию email.
    """

    VERIFICATION_TOKEN_TTL_HOURS: int = 24

    def __init__(
        self,
        user_repo: UserRepository,
        user_auth_repo: UserAuthRepository,
        role_repo: RoleRepository,
        password_port: PasswordPort,
        event_bus: DomainEventBus,
        notification_port: IdentityNotificationPort,
    ) -> None:
        super().__init__()
        self._user_repo = user_repo
        self._user_auth_repo = user_auth_repo
        self._role_repo = role_repo
        self._password_port = password_port
        self._event_bus = event_bus
        self._notification_port = notification_port

    async def handle(self, command: RegisterUserCommand) -> UserDTO:
        email = Email(command.email)
        provider = AuthProvider(command.auth_provider)

        existing = await self._user_repo.get_by_email(email)
        if existing is not None:
            raise UserAlreadyExistsException(command.email)

        user = User.register(email=email, auth_provider=provider)

        default_role = await self._role_repo.get_by_name("user")
        if default_role is not None:
            user.assign_role(default_role.id)

        hashed = self._password_port.hash_password(command.password)
        user_auth = UserAuth.create_for_email_auth(
            user_id=user.id,
            email=email,
            password_hash=PasswordHash(value=hashed),
        )

        token_value = str(uuid.uuid4())
        expires_at = datetime.now(tz=timezone.utc) + timedelta(hours=self.VERIFICATION_TOKEN_TTL_HOURS)
        token = VerificationToken(
            value=token_value,
            token_type=VerificationType.EMAIL_CONFIRMATION,
            expires_at=expires_at,
        )
        user_auth.request_email_verification(token=token, expires_at=expires_at)

        await self._user_repo.add(user)
        await self._user_auth_repo.add(user_auth)

        await self._event_bus.publish_all(user.clear_domain_events())
        await self._event_bus.publish_all(user_auth.clear_domain_events())

        await self._notification_port.send_email_verification(
            email=command.email,
            user_id=str(user.id),
            token=token_value,
        )

        return UserDTO(
            id=str(user.id),
            email=user.email.value,
            status=user.status.value,
            role_ids=[str(rid) for rid in user.role_ids],
            is_email_confirmed=user.is_email_confirmed,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
