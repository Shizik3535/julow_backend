from __future__ import annotations

from app.context.identity.application.dto.sso_config_dto import SSOConfigDTO
from app.context.identity.application.ports.integration.inboard.organization_sso_port import (
    OrganizationSSOPort,
)
from app.context.organization.application.ports.integration.outboard.organization_sso_provider import (
    OrganizationSSOProvider,
)


class OrganizationSSOAdapter(OrganizationSSOPort):
    """
    Inboard-адаптер: получение SSO-конфигурации из Organization BC.

    Делегирует в OrganizationSSOProvider (outboard Organization BC),
    маппит в Identity-local SSOConfigDTO.
    """

    def __init__(self, org_sso_provider: OrganizationSSOProvider) -> None:
        self._org_sso_provider = org_sso_provider

    async def get_sso_config_by_email_domain(self, email_domain: str) -> SSOConfigDTO | None:
        org_dto = await self._org_sso_provider.get_sso_config_by_email_domain(email_domain)
        if org_dto is None:
            return None
        return SSOConfigDTO(
            org_id=org_dto.org_id,
            provider=org_dto.provider,
            entity_id=org_dto.entity_id,
            sso_url=org_dto.sso_url,
            certificate=org_dto.certificate,
            enforce_sso=org_dto.enforce_sso,
            auto_provision=org_dto.auto_provision,
            default_role_id=org_dto.default_role_id,
            group_mapping=org_dto.group_mapping,
            attribute_mapping=org_dto.attribute_mapping,
            email_domains=org_dto.email_domains,
        )

    async def is_sso_enforced(self, email_domain: str) -> bool:
        return await self._org_sso_provider.is_sso_enforced_for_domain(email_domain)
