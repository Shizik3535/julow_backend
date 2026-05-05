from __future__ import annotations

from abc import abstractmethod

from app.shared.domain.base_repository import RepositoryPort
from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.domain.aggregates.sso_integration import SSOIntegration
from app.context.organization.domain.value_objects.sso_provider import SSOProvider


class SSOIntegrationRepository(RepositoryPort[SSOIntegration]):
    """
    Порт репозитория для агрегата SSOIntegration.

    Расширяет базовый RepositoryPort специфичными запросами
    для управления SSO-интеграциями.
    """

    @abstractmethod
    async def get_by_org_id(self, org_id: Id) -> list[SSOIntegration]:
        """Получить все SSO-интеграции организации."""

    @abstractmethod
    async def get_by_org_and_provider(self, org_id: Id, provider: SSOProvider) -> SSOIntegration | None:
        """Найти SSO-интеграцию по org_id и провайдеру."""

    @abstractmethod
    async def get_active_by_email_domain(self, email_domain: str) -> SSOIntegration | None:
        """Найти активную SSO-интеграцию по email-домену."""
