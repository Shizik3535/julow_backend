from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.context.identity.application.dto.sso_initiate_dto import SSOInitiateDTO
from app.context.identity.application.ports.integration.inboard.organization_sso_port import (
    OrganizationSSOPort,
)
from app.context.identity.application.ports.sso.sso_port import SSOPort
from app.context.identity.infrastructure.sso.exceptions import SSOAuthenticationException


class InitiateSSOLoginCommand(BaseCommand):
    """
    Команда инициации SSO-логина.

    По email определяет домен, находит SSO-конфигурацию организации
    и возвращает URL для редиректа на IdP.

    Атрибуты:
        email: Email пользователя.
        callback_url: URL обратного вызова после аутентификации на IdP.
    """

    email: str
    callback_url: str


class InitiateSSOLoginHandler(BaseCommandHandler[InitiateSSOLoginCommand, SSOInitiateDTO]):
    """
    Обработчик инициации SSO-логина.

    Определяет SSO-конфигурацию по email-домену и генерирует
    redirect URL для аутентификации на IdP.
    """

    def __init__(
        self,
        org_sso_port: OrganizationSSOPort,
        sso_port: SSOPort,
    ) -> None:
        super().__init__()
        self._org_sso_port = org_sso_port
        self._sso_port = sso_port

    async def handle(self, command: InitiateSSOLoginCommand) -> SSOInitiateDTO:
        # 1. Извлечь домен из email
        email_domain = command.email.split("@")[-1].lower()

        # 2. Получить SSO-конфигурацию по домену
        sso_config = await self._org_sso_port.get_sso_config_by_email_domain(email_domain)
        if sso_config is None:
            raise SSOAuthenticationException(
                f"SSO не настроен для домена {email_domain}"
            )

        # 3. Проверить поддержку протокола
        if not self._sso_port.supports_protocol(sso_config.provider):
            raise SSOAuthenticationException(
                f"Протокол SSO '{sso_config.provider}' не поддерживается"
            )

        # 4. Сгенерировать redirect URL
        redirect_url = self._sso_port.build_auth_request(
            provider=sso_config.provider,
            entity_id=sso_config.entity_id,
            sso_url=sso_config.sso_url,
            certificate=sso_config.certificate,
            callback_url=command.callback_url,
            attribute_mapping=sso_config.attribute_mapping,
        )

        return SSOInitiateDTO(
            redirect_url=redirect_url,
            state=None,
        )
