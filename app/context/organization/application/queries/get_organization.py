from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.application.dto.organization_dto import OrganizationDTO
from app.context.organization.application.ports.authorization.org_permission_checker_port import OrgPermissionCheckerPort
from app.context.organization.domain.exceptions.organization_exceptions import OrganizationNotFoundException
from app.context.organization.domain.repositories.organization_repository import OrganizationRepository


class GetOrganizationQuery(BaseQuery):
    """
    Запрос организации по ID.

    Атрибуты:
        org_id: Идентификатор организации.
    """

    caller_id: str
    org_id: str


class GetOrganizationHandler(BaseQueryHandler[GetOrganizationQuery, OrganizationDTO]):
    """Обработчик запроса организации по ID."""

    REQUIRED_PERMISSION = "org.read"

    def __init__(self, org_repo: OrganizationRepository, org_permission_checker: OrgPermissionCheckerPort) -> None:
        super().__init__()
        self._org_repo = org_repo
        self._org_permission_checker = org_permission_checker

    async def handle(self, query: GetOrganizationQuery) -> OrganizationDTO:
        org_id = Id.from_string(query.org_id)

        org = await self._org_repo.get_by_id(org_id)
        if org is None:
            raise OrganizationNotFoundException(query.org_id)

        await self._org_permission_checker.require_permission(
            Id.from_string(query.caller_id), org_id, self.REQUIRED_PERMISSION,
        )

        return OrganizationDTO(
            id=str(org.id),
            name=org.name,
            status=org.status.value,
            owner_ids=[str(oid) for oid in org.owner_ids],
            personalization={
                "color": org.personalization.color.hex if org.personalization.color else None,
                "icon_url": str(org.personalization.icon_url) if org.personalization.icon_url else None,
                "display_name": org.personalization.display_name,
                "custom_domain": org.personalization.custom_domain,
                "branding": (
                    {
                        "logo_url": str(org.personalization.branding.logo_url) if org.personalization.branding.logo_url else None,
                        "favicon_url": str(org.personalization.branding.favicon_url) if org.personalization.branding.favicon_url else None,
                        "custom_css": org.personalization.branding.custom_css,
                        "login_message": org.personalization.branding.login_message,
                    }
                    if org.personalization.branding
                    else None
                ),
            },
            security_policy={
                "require_2fa": org.security_policy.require_2fa,
                "password_min_length": org.security_policy.password_min_length,
                "session_timeout_minutes": org.security_policy.session_timeout_minutes,
                "ip_allowlist": org.security_policy.ip_allowlist,
                "domain_restrictions": org.security_policy.domain_restrictions,
                "require_email_verification": org.security_policy.require_email_verification,
            },
            membership_policy={
                "allow_invitation_links": org.membership_policy.allow_invitation_links,
                "default_role": org.membership_policy.default_role,
                "require_approval": org.membership_policy.require_approval,
                "max_members": org.membership_policy.max_members,
                "allowed_email_domains": org.membership_policy.allowed_email_domains,
            },
            created_at=org.created_at,
            updated_at=org.updated_at,
        )
