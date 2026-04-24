from __future__ import annotations

from dataclasses import dataclass

from app.shared.domain.base_domain_event import BaseDomainEvent
from app.context.organization.domain.value_objects.sso_provider import SSOProvider


@dataclass(frozen=True)
class SSOIntegrationAdded(BaseDomainEvent):
    """SSO-интеграция добавлена."""

    org_id: str = ""
    provider: SSOProvider = SSOProvider.SAML


@dataclass(frozen=True)
class SSOIntegrationUpdated(BaseDomainEvent):
    """SSO-интеграция обновлена."""

    org_id: str = ""
    provider: SSOProvider = SSOProvider.SAML


@dataclass(frozen=True)
class SSOIntegrationDeactivated(BaseDomainEvent):
    """SSO-интеграция деактивирована."""

    org_id: str = ""
    provider: SSOProvider = SSOProvider.SAML
