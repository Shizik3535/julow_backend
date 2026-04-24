from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.application.ports.auth.auth_port import AuthTokenPort
from app.shared.application.ports.auth.password_port import PasswordPort
from app.shared.domain.value_objects.email_vo import Email
from app.shared.domain.value_objects.ip_address_vo import IpAddress
from app.context.identity.application.dto.auth_result_dto import AuthResultDTO
from app.context.identity.application.dto.user_dto import UserDTO
from app.context.identity.application.exceptions.auth_app_exceptions import (
    AccountLockedException,
    AuthenticationFailedException,
)
from app.context.identity.domain.aggregates.session import Session
from app.context.identity.domain.repositories.session_repository import SessionRepository
from app.context.identity.domain.repositories.user_auth_repository import UserAuthRepository
from app.context.identity.domain.repositories.user_repository import UserRepository
from app.context.identity.domain.value_objects.device_info import DeviceInfo
from app.context.identity.domain.value_objects.failed_login_policy import FailedLoginPolicy
from app.context.identity.domain.value_objects.password_hash import PasswordHash
from app.context.identity.domain.value_objects.refresh_token import RefreshToken


class LoginUserCommand(BaseCommand):
    """
    Команда входа пользователя.

    Атрибуты:
        email: Email-адрес.
        password: Пароль в открытом виде.
        ip: IP-адрес клиента.
        user_agent: User-Agent клиента.
        is_remember_me: Флаг «Запомнить меня».
    """

    email: str
    password: str
    ip: str = "127.0.0.1"
    user_agent: str = "unknown"
    is_remember_me: bool = False


class LoginUserHandler(BaseCommandHandler[LoginUserCommand, AuthResultDTO]):
    """
    Обработчик входа пользователя.

    Проверяет credentials, записывает попытку входа,
    создаёт сессию и возвращает токены.
    """

    def __init__(
        self,
        user_repo: UserRepository,
        user_auth_repo: UserAuthRepository,
        session_repo: SessionRepository,
        password_port: PasswordPort,
        auth_token_port: AuthTokenPort,
        failed_login_policy: FailedLoginPolicy,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._user_repo = user_repo
        self._user_auth_repo = user_auth_repo
        self._session_repo = session_repo
        self._password_port = password_port
        self._auth_token_port = auth_token_port
        self._failed_login_policy = failed_login_policy
        self._event_bus = event_bus

    async def handle(self, command: LoginUserCommand) -> AuthResultDTO:
        email = Email(command.email)

        user_auth = await self._user_auth_repo.get_by_email(email)
        if user_auth is None:
            raise AuthenticationFailedException()

        if user_auth.is_locked():
            locked_until = user_auth.locked_until.isoformat() if user_auth.locked_until else None
            raise AccountLockedException(locked_until)

        if user_auth.password_hash is None:
            raise AuthenticationFailedException()

        is_valid = self._password_port.verify_password(
            command.password, user_auth.password_hash.value
        )
        if not is_valid:
            user_auth.record_failed_login(self._failed_login_policy)
            await self._user_auth_repo.update(user_auth)
            raise AuthenticationFailedException()

        user = await self._user_repo.get_by_email(email)
        if user is None:
            raise AuthenticationFailedException()

        token_pair = self._auth_token_port.generate_token_pair(str(user.id))

        session = Session.create(
            user_id=user.id,
            device_info=DeviceInfo(user_agent=command.user_agent),
            ip_address=IpAddress(command.ip),
            is_remember_me=command.is_remember_me,
            refresh_token=RefreshToken(value=token_pair.refresh_token),
        )

        user_auth.record_successful_login(
            session_id=str(session.id),
            ip=IpAddress(command.ip),
            device=command.user_agent,
        )

        await self._user_auth_repo.update(user_auth)
        await self._session_repo.add(session)

        await self._event_bus.publish_all(user_auth.clear_domain_events())
        await self._event_bus.publish_all(session.clear_domain_events())

        return AuthResultDTO(
            user=UserDTO(
                id=str(user.id),
                email=user.email.value,
                status=user.status.value,
                role_ids=[str(rid) for rid in user.role_ids],
                is_email_confirmed=user.is_email_confirmed,
                created_at=user.created_at,
                updated_at=user.updated_at,
            ),
            access_token=token_pair.access_token,
            refresh_token=token_pair.refresh_token,
            access_expires_in=token_pair.access_expires_in,
            refresh_expires_in=token_pair.refresh_expires_in,
        )
