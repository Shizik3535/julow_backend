from __future__ import annotations

from app.context.organization.application.dto.sso_config_dto import SSOConfigDTO
from app.context.organization.application.ports.encryption.encryption_port import EncryptionPort
from app.context.organization.application.ports.integration.outboard.organization_sso_provider import (
    OrganizationSSOProvider,
)
from app.context.organization.domain.repositories.organization_repository import OrganizationRepository
from app.context.organization.domain.repositories.sso_integration_repository import SSOIntegrationRepository


class OrganizationSSOProviderAdapter(OrganizationSSOProvider):
    """Реализация OrganizationSSOProvider (outboard) — предоставляет SSO-конфигурацию другим BC."""

    def __init__(
        self,
        sso_repo: SSOIntegrationRepository,
        org_repo: OrganizationRepository,
        encryption_port: EncryptionPort,
    ) -> None:
        self._sso_repo = sso_repo
        self._org_repo = org_repo
        self._encryption_port = encryption_port

    async def get_sso_config_by_email_domain(self, email_domain: str) -> SSOConfigDTO | None:
        integration = await self._sso_repo.get_active_by_email_domain(email_domain)
        if integration is None:
            return None

        org = await self._org_repo.get_by_id(integration.org_id)
        if org is None:
            return None

        decrypted_cert = await self._encryption_port.decrypt(integration.certificate)

        return SSOConfigDTO(
            org_id=str(integration.org_id),
            provider=integration.provider.value,
            entity_id=integration.entity_id,
            sso_url=integration.sso_url,
            certificate=decrypted_cert,
            enforce_sso=org.security_policy.enforce_sso,
            auto_provision=integration.auto_provision,
            default_role_id=str(integration.default_role_id) if integration.default_role_id else None,
            group_mapping=integration.group_mapping,
            attribute_mapping=integration.attribute_mapping,
            email_domains=integration.email_domains,
        )

    async def is_sso_enforced_for_domain(self, email_domain: str) -> bool:
        integration = await self._sso_repo.get_active_by_email_domain(email_domain)
        if integration is None:
            return False
        org = await self._org_repo.get_by_id(integration.org_id)
        if org is None:
            return False
        return org.security_policy.enforce_sso
