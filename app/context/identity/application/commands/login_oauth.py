from __future__ import annotations

import re

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.application.ports.auth.auth_port import AuthTokenPort
from app.shared.domain.value_objects.email_vo import Email
from app.shared.domain.value_objects.id_vo import Id
from app.shared.domain.value_objects.ip_address_vo import IpAddress
from app.context.identity.application.dto.auth_result_dto import AuthResultDTO
from app.context.identity.application.dto.user_dto import UserDTO
from app.context.identity.application.exceptions.auth_app_exceptions import (
    AccountLockedException,
    AuthenticationFailedException,
)
from app.context.identity.application.ports.oauth.oauth_port import OAuthPort
from app.context.identity.domain.aggregates.session import Session
from app.context.identity.domain.aggregates.user import User
from app.context.identity.domain.aggregates.user_auth import UserAuth
from app.context.identity.domain.repositories.role_repository import RoleRepository
from app.context.identity.domain.repositories.session_repository import SessionRepository
from app.context.identity.domain.repositories.user_auth_repository import UserAuthRepository
from app.context.identity.domain.repositories.user_repository import UserRepository
from app.context.identity.domain.value_objects.auth_provider import AuthProvider
from app.context.identity.domain.value_objects.device_info import DeviceInfo
from app.context.identity.domain.value_objects.failed_login_policy import FailedLoginPolicy
from app.context.identity.domain.value_objects.refresh_token import RefreshToken


class LoginOAuthCommand(BaseCommand):
    """
    Команда входа через OAuth-провайдер.

    Атрибуты:
        provider: Название провайдера (oauth_google, oauth_github, ...).
        authorization_code: Authorization code от провайдера.
        redirect_uri: URI перенаправления.
        ip: IP-адрес клиента.
        user_agent: User-Agent клиента.
        is_remember_me: Флаг «Запомнить меня».
    """

    provider: str
    authorization_code: str
    redirect_uri: str
    ip: str = "127.0.0.1"
    user_agent: str = "unknown"
    is_remember_me: bool = False


class LoginOAuthHandler(BaseCommandHandler[LoginOAuthCommand, AuthResultDTO]):
    """
    Обработчик входа через OAuth-провайдер.

    Обменивает authorization code на access token, получает профиль
    пользователя от провайдера. Если пользователь уже привязан —
    логинит. Если email совпадает с существующим аккаунтом —
    привязывает OAuth и логинит. Если новый — авто-регистрация.
    """

    def __init__(
        self,
        user_repo: UserRepository,
        user_auth_repo: UserAuthRepository,
        session_repo: SessionRepository,
        role_repo: RoleRepository,
        oauth_port: OAuthPort,
        auth_token_port: AuthTokenPort,
        failed_login_policy: FailedLoginPolicy,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._user_repo = user_repo
        self._user_auth_repo = user_auth_repo
        self._session_repo = session_repo
        self._role_repo = role_repo
        self._oauth_port = oauth_port
        self._auth_token_port = auth_token_port
        self._failed_login_policy = failed_login_policy
        self._event_bus = event_bus

    async def handle(self, command: LoginOAuthCommand) -> AuthResultDTO:
        provider = AuthProvider(command.provider)

        # 1. Обменять authorization code на access token
        access_token = await self._oauth_port.exchange_code(
            provider=command.provider,
            code=command.authorization_code,
            redirect_uri=command.redirect_uri,
        )

        # 2. Получить профиль от провайдера
        user_info = await self._oauth_port.get_user_info(
            provider=command.provider,
            access_token=access_token,
        )

        # 3. Найти UserAuth по OAuth-провайдеру
        user_auth = await self._user_auth_repo.get_by_oauth_provider(
            provider=provider,
            provider_user_id=user_info.provider_user_id,
        )

        if user_auth is not None:
            # Пользователь уже привязан — логин
            return await self._login_existing(user_auth, command)

        # 4. Попытка найти по email от провайдера
        if user_info.email:
            email = Email(user_info.email)
            user_auth = await self._user_auth_repo.get_by_email(email)

            if user_auth is not None:
                # Привязать OAuth к существующему аккаунту
                user_auth.link_oauth(
                    provider=provider,
                    provider_user_id=user_info.provider_user_id,
                    email=user_info.email,
                    display_name=user_info.display_name,
                )
                await self._user_auth_repo.update(user_auth)
                await self._event_bus.publish_all(user_auth.clear_domain_events())
                return await self._login_existing(user_auth, command)

        # 5. Авто-регистрация нового пользователя
        return await self._auto_register(user_info, provider, command)

    async def _login_existing(
        self, user_auth: UserAuth, command: LoginOAuthCommand
    ) -> AuthResultDTO:
        """Логин существующего пользователя с OAuth-привязкой."""
        if user_auth.is_locked():
            locked_until = user_auth.locked_until.isoformat() if user_auth.locked_until else None
            raise AccountLockedException(locked_until)

        user = await self._user_repo.get_by_id(user_auth.user_id)
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

    def _build_fallback_email(self, provider: AuthProvider, provider_user_id: str) -> Email:
        provider_label = provider.value.replace("_", "-")
        local_part = re.sub(r"[^a-zA-Z0-9._%+-]+", "-", provider_user_id).strip(".-")
        if not local_part:
            local_part = "oauth-user"
        return Email(f"{local_part}@{provider_label}.invalid")

    async def _auto_register(
        self,
        user_info,
        provider: AuthProvider,
        command: LoginOAuthCommand,
    ) -> AuthResultDTO:
        """Авто-регистрация нового пользователя через OAuth."""
        email = (
            Email(user_info.email)
            if user_info.email
            else self._build_fallback_email(provider, user_info.provider_user_id)
        )

        user = User.register_via_oauth(email=email, auth_provider=provider)

        default_role = await self._role_repo.get_by_name("user")
        if default_role is not None:
            user.assign_role(default_role.id)

        user_auth = UserAuth.create_for_oauth(
            user_id=user.id,
            email=email,
            provider=provider,
            provider_user_id=user_info.provider_user_id,
        )

        await self._user_repo.add(user)
        await self._user_auth_repo.add(user_auth)

        await self._event_bus.publish_all(user.clear_domain_events())
        await self._event_bus.publish_all(user_auth.clear_domain_events())

        # Сразу логиним
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
