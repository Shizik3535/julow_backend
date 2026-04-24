from __future__ import annotations

from app.shared.domain.value_objects.id_vo import Id
from app.shared.domain.value_objects.url_vo import Url
from app.shared.infrastructure.persistence.sqlalchemy_base_mapper import BaseMapper

from app.context.organization.domain.aggregates.organization import Organization
from app.context.organization.domain.value_objects.accent_color import AccentColor
from app.context.organization.domain.value_objects.membership_policy import MembershipPolicy
from app.context.organization.domain.value_objects.org_branding import OrgBranding
from app.context.organization.domain.value_objects.org_personalization import OrgPersonalization
from app.context.organization.domain.value_objects.org_status import OrgStatus
from app.context.organization.domain.value_objects.security_policy import SecurityPolicy
from app.context.organization.infrastructure.persistence.orm_models.organization_orm import (
    OrganizationORM,
)


class OrganizationMapper(BaseMapper[Organization, OrganizationORM]):
    """Data Mapper: Organization ↔ OrganizationORM."""

    # ------------------------------------------------------------------
    # ORM → Domain
    # ------------------------------------------------------------------

    def to_domain(self, orm_model: OrganizationORM) -> Organization:
        # OrgBranding
        branding = None
        if any([
            orm_model.pers_branding_logo_url,
            orm_model.pers_branding_favicon_url,
            orm_model.pers_branding_custom_css,
            orm_model.pers_branding_login_message,
        ]):
            branding = OrgBranding(
                logo_url=Url(orm_model.pers_branding_logo_url) if orm_model.pers_branding_logo_url else None,
                favicon_url=Url(orm_model.pers_branding_favicon_url) if orm_model.pers_branding_favicon_url else None,
                custom_css=orm_model.pers_branding_custom_css,
                login_message=orm_model.pers_branding_login_message,
            )

        # OrgPersonalization
        personalization = OrgPersonalization(
            color=AccentColor(hex=orm_model.pers_color_hex) if orm_model.pers_color_hex else None,
            icon_url=Url(orm_model.pers_icon_url) if orm_model.pers_icon_url else None,
            display_name=orm_model.pers_display_name,
            custom_domain=orm_model.pers_custom_domain,
            branding=branding,
        )

        # SecurityPolicy
        security_policy = SecurityPolicy(
            require_2fa=orm_model.sp_require_2fa,
            password_min_length=orm_model.sp_password_min_length,
            session_timeout_minutes=orm_model.sp_session_timeout_minutes,
            ip_allowlist=orm_model.sp_ip_allowlist or [],
            domain_restrictions=orm_model.sp_domain_restrictions or [],
            require_email_verification=orm_model.sp_require_email_verification,
        )

        # MembershipPolicy
        membership_policy = MembershipPolicy(
            allow_invitation_links=orm_model.mp_allow_invitation_links,
            default_role=orm_model.mp_default_role,
            require_approval=orm_model.mp_require_approval,
            max_members=orm_model.mp_max_members,
            allowed_email_domains=orm_model.mp_allowed_email_domains or [],
        )

        return Organization(
            id=self._map_id(orm_model.id),
            name=orm_model.name,
            status=OrgStatus(orm_model.status),
            personalization=personalization,
            owner_ids=[],  # owner_ids маппятся в repo через association table
            security_policy=security_policy,
            membership_policy=membership_policy,
            created_at=orm_model.created_at,
            updated_at=orm_model.updated_at,
        )

    # ------------------------------------------------------------------
    # Domain → ORM
    # ------------------------------------------------------------------

    def to_orm(self, aggregate: Organization) -> OrganizationORM:
        pers = aggregate.personalization
        sp = aggregate.security_policy
        mp = aggregate.membership_policy

        return OrganizationORM(
            id=self._map_uuid(aggregate.id),
            name=aggregate.name,
            status=aggregate.status.value,
            # OrgPersonalization
            pers_color_hex=str(pers.color) if pers.color else None,
            pers_icon_url=str(pers.icon_url) if pers.icon_url else None,
            pers_display_name=pers.display_name,
            pers_custom_domain=pers.custom_domain,
            # OrgBranding
            pers_branding_logo_url=str(pers.branding.logo_url) if pers.branding and pers.branding.logo_url else None,
            pers_branding_favicon_url=str(pers.branding.favicon_url) if pers.branding and pers.branding.favicon_url else None,
            pers_branding_custom_css=pers.branding.custom_css if pers.branding else None,
            pers_branding_login_message=pers.branding.login_message if pers.branding else None,
            # SecurityPolicy
            sp_require_2fa=sp.require_2fa,
            sp_password_min_length=sp.password_min_length,
            sp_session_timeout_minutes=sp.session_timeout_minutes,
            sp_ip_allowlist=sp.ip_allowlist if sp.ip_allowlist else None,
            sp_domain_restrictions=sp.domain_restrictions if sp.domain_restrictions else None,
            sp_require_email_verification=sp.require_email_verification,
            # MembershipPolicy
            mp_allow_invitation_links=mp.allow_invitation_links,
            mp_default_role=mp.default_role,
            mp_require_approval=mp.require_approval,
            mp_max_members=mp.max_members,
            mp_allowed_email_domains=mp.allowed_email_domains if mp.allowed_email_domains else None,
            # Timestamps
            created_at=aggregate.created_at,
            updated_at=aggregate.updated_at,
        )
