from __future__ import annotations

from abc import ABC, abstractmethod

from app.context.organization.application.dto.sso_config_dto import SSOConfigDTO


class OrganizationSSOProvider(ABC):
    """
    Outboard-порт: предоставляет SSO-конфигурацию другим BC.

    Identity BC потребляет этот порт для получения SSO-конфига
    организации при инициации SSO-логина.
    """

    @abstractmethod
    async def get_sso_config_by_email_domain(self, email_domain: str) -> SSOConfigDTO | None:
        """
        Получить SSO-конфигурацию по email-домену.

        Аргументы:
            email_domain: Домен email (например, company.com).

        Возвращает:
            SSOConfigDTO или None, если SSO не настроен для этого домена.
        """

    @abstractmethod
    async def is_sso_enforced_for_domain(self, email_domain: str) -> bool:
        """
        Проверить, обязателен ли SSO-вход для email-домена.

        Аргументы:
            email_domain: Домен email.

        Возвращает:
            True, если enforce_sso включён для организации с этим доменом.
        """
