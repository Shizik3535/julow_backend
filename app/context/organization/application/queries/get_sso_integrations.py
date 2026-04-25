from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.application.dto.sso_integration_dto import SSOIntegrationDTO, SSOIntegrationListDTO
from app.context.organization.application.ports.authorization.org_permission_checker_port import OrgPermissionCheckerPort
from app.context.organization.domain.exceptions.organization_exceptions import OrganizationNotFoundException
from app.context.organization.domain.repositories.organization_repository import OrganizationRepository
from app.context.organization.domain.repositories.sso_integration_repository import SSOIntegrationRepository


class GetSSOIntegrationsQuery(BaseQuery):
    """
    Запрос SSO-интеграций организации.

    Атрибуты:
        org_id: ID организации.
    """

    caller_id: str
    org_id: str


class GetSSOIntegrationsHandler(BaseQueryHandler[GetSSOIntegrationsQuery, SSOIntegrationListDTO]):
    """Обработчик запроса SSO-интеграций организации."""

    REQUIRED_PERMISSION = "org.settings.read"

    def __init__(self, sso_repo: SSOIntegrationRepository, org_repo: OrganizationRepository, org_permission_checker: OrgPermissionCheckerPort) -> None:
        super().__init__()
        self._sso_repo = sso_repo
        self._org_repo = org_repo
        self._org_permission_checker = org_permission_checker

    async def handle(self, query: GetSSOIntegrationsQuery) -> SSOIntegrationListDTO:
        org_id = Id.from_string(query.org_id)

        org = await self._org_repo.get_by_id(org_id)
        if org is None:
            raise OrganizationNotFoundException(query.org_id)
        await self._org_permission_checker.require_permission(
            Id.from_string(query.caller_id), org_id, self.REQUIRED_PERMISSION,
        )

        integrations = await self._sso_repo.get_by_org_id(org_id)

        items = [
            SSOIntegrationDTO(
                id=str(i.id),
                org_id=str(i.org_id),
                provider=i.provider.value,
                entity_id=i.entity_id,
                sso_url=i.sso_url,
                is_active=i.is_active,
                group_mapping=i.group_mapping,
                attribute_mapping=i.attribute_mapping,
                added_at=i.added_at,
                added_by=str(i.added_by),
                created_at=i.created_at,
                updated_at=i.updated_at,
            )
            for i in integrations
        ]
        return SSOIntegrationListDTO(items=items, total=len(items))
