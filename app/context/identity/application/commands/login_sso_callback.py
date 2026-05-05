from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.application.ports.auth.auth_port import AuthTokenPort
from app.shared.domain.value_objects.email_vo import Email
from app.shared.domain.value_objects.ip_address_vo import IpAddress
from app.context.identity.application.dto.auth_result_dto import AuthResultDTO
from app.context.identity.application.dto.user_dto import UserDTO
from app.context.identity.application.exceptions.auth_app_exceptions import (
    AccountLockedException,
    AuthenticationFailedException,
)
from app.context.identity.application.ports.integration.inboard.organization_sso_port import (
    OrganizationSSOPort,
)
from app.context.identity.application.ports.sso.sso_port import SSOPort, SSOUserInfo
from app.context.identity.domain.aggregates.session import Session
from app.context.identity.domain.aggregates.user import User
from app.context.identity.domain.aggregates.user_auth import UserAuth
from app.context.identity.domain.events.auth_events import SSOLinked
from app.context.identity.domain.repositories.role_repository import RoleRepository
from app.context.identity.domain.repositories.session_repository import SessionRepository
from app.context.identity.domain.repositories.user_auth_repository import UserAuthRepository
from app.context.identity.domain.repositories.user_repository import UserRepository
from app.context.identity.domain.value_objects.auth_provider import AuthProvider
from app.context.identity.domain.value_objects.device_info import DeviceInfo
from app.context.identity.domain.value_objects.refresh_token import RefreshToken
from app.context.identity.infrastructure.sso.exceptions import SSOAuthenticationException


class LoginSSOCallbackCommand(BaseCommand):
    """
    Команда обработки callback от SSO IdP.

    Атрибуты:
        email_domain: Домен email (для определения SSO-конфигурации).
        response_data: Данные ответа от IdP (SAMLResponse, code и т.д.).
        callback_url: URL обратного вызова (должен совпадать с тем, что при инициации).
        ip: IP-адрес клиента.
        user_agent: User-Agent клиента.
        is_remember_me: Флаг «Запомнить меня».
    """

    email_domain: str
    response_data: dict
    callback_url: str
    ip: str = "127.0.0.1"
    user_agent: str = "unknown"
    is_remember_me: bool = False


class LoginSSOCallbackHandler(BaseCommandHandler[LoginSSOCallbackCommand, AuthResultDTO]):
    """
    Обработчик callback от SSO IdP.

    Обрабатывает ответ IdP, находит/создаёт пользователя,
    создаёт сессию, публикует события auto-provisioning.
    """

    def __init__(
        self,
        user_repo: UserRepository,
        user_auth_repo: UserAuthRepository,
        session_repo: SessionRepository,
        role_repo: RoleRepository,
        org_sso_port: OrganizationSSOPort,
        sso_port: SSOPort,
        auth_token_port: AuthTokenPort,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._user_repo = user_repo
        self._user_auth_repo = user_auth_repo
        self._session_repo = session_repo
        self._role_repo = role_repo
        self._org_sso_port = org_sso_port
        self._sso_port = sso_port
        self._auth_token_port = auth_token_port
        self._event_bus = event_bus

    async def handle(self, command: LoginSSOCallbackCommand) -> AuthResultDTO:
        # 1. Получить SSO-конфигурацию
        sso_config = await self._org_sso_port.get_sso_config_by_email_domain(command.email_domain)
        if sso_config is None:
            raise SSOAuthenticationException(
                f"SSO не настроен для домена {command.email_domain}"
            )

        # 2. Обработать ответ от IdP
        sso_user_info = await self._sso_port.process_response(
            provider=sso_config.provider,
            entity_id=sso_config.entity_id,
            sso_url=sso_config.sso_url,
            certificate=sso_config.certificate,
            callback_url=command.callback_url,
            response_data=command.response_data,
            attribute_mapping=sso_config.attribute_mapping,
        )

        # 3. Найти UserAuth по SSO provider_user_id
        user_auth = await self._user_auth_repo.get_by_oauth_provider(
            provider=AuthProvider.SAML_SSO,
            provider_user_id=sso_user_info.provider_user_id,
        )

        if user_auth is not None:
            # Пользователь уже привязан — логин
            return await self._login_existing(user_auth, command, sso_config.org_id)

        # 4. Попытка найти по email
        if sso_user_info.email:
            email = Email(sso_user_info.email)
            user_auth = await self._user_auth_repo.get_by_email(email)

            if user_auth is not None:
                # Привязать SSO к существующему аккаунту
                user_auth.link_oauth(
                    provider=AuthProvider.SAML_SSO,
                    provider_user_id=sso_user_info.provider_user_id,
                    email=sso_user_info.email,
                    display_name=sso_user_info.display_name,
                )
                await self._user_auth_repo.update(user_auth)
                await self._event_bus.publish_all(user_auth.clear_domain_events())
                return await self._login_existing(user_auth, command, sso_config.org_id)

        # 5. Авто-регистрация нового пользователя
        return await self._auto_register(sso_user_info, sso_config, command)

    async def _login_existing(
        self,
        user_auth: UserAuth,
        command: LoginSSOCallbackCommand,
        org_id: str,
    ) -> AuthResultDTO:
        """Логин существующего пользователя через SSO."""
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

    async def _auto_register(
        self,
        sso_user_info: SSOUserInfo,
        sso_config,
        command: LoginSSOCallbackCommand,
    ) -> AuthResultDTO:
        """Авто-регистрация нового пользователя через SSO."""
        email = Email(sso_user_info.email) if sso_user_info.email else Email(
            f"{sso_user_info.provider_user_id}@sso"
        )

        user = User.register_via_oauth(email=email, auth_provider=AuthProvider.SAML_SSO)

        default_role = await self._role_repo.get_by_name("user")
        if default_role is not None:
            user.assign_role(default_role.id)

        user_auth = UserAuth.create_for_sso(
            user_id=user.id,
            email=email,
            provider_user_id=sso_user_info.provider_user_id,
        )

        await self._user_repo.add(user)
        await self._user_auth_repo.add(user_auth)

        await self._event_bus.publish_all(user.clear_domain_events())
        await self._event_bus.publish_all(user_auth.clear_domain_events())

        # Публикуем событие для auto-provisioning в Organization BC
        if sso_config.auto_provision:
            from app.context.identity.domain.events.auth_events import SSOUserProvisioned
            await self._event_bus.publish_all([
                SSOUserProvisioned(
                    user_id=str(user.id),
                    org_id=sso_config.org_id,
                    email=email.value,
                    default_role_id=sso_config.default_role_id or "",
                )
            ])

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
