"""
Organization BC conftest — фикстуры для unit-тестов Organization BC.

Содержит фабричные фикстуры для агрегатов, VOs и политик,
используемых в нескольких тестовых модулях.
"""

import pytest

from app.shared.domain.value_objects.email_vo import Email
from app.shared.domain.value_objects.id_vo import Id
from app.shared.domain.value_objects.url_vo import Url
from app.context.organization.domain.aggregates.department import Department
from app.context.organization.domain.aggregates.invitation import Invitation
from app.context.organization.domain.aggregates.org_membership import OrgMembership
from app.context.organization.domain.aggregates.org_role import OrgRole
from app.context.organization.domain.aggregates.organization import Organization
from app.context.organization.domain.aggregates.sso_integration import SSOIntegration
from app.context.organization.domain.aggregates.storage_integration import StorageIntegration
from app.context.organization.domain.aggregates.team import Team
from app.context.organization.domain.value_objects.accent_color import AccentColor
from app.context.organization.domain.value_objects.invitation_token import InvitationToken
from app.context.organization.domain.value_objects.org_branding import OrgBranding
from app.context.organization.domain.value_objects.org_personalization import OrgPersonalization
from app.context.organization.domain.value_objects.org_role_scope import OrgRoleScope
from app.context.organization.domain.value_objects.security_policy import SecurityPolicy
from app.context.organization.domain.value_objects.sso_provider import SSOProvider
from app.context.organization.domain.value_objects.storage_config import StorageConfig
from app.context.organization.domain.value_objects.storage_provider import StorageProvider
from app.context.organization.domain.value_objects.storage_quota import StorageQuota
from app.context.organization.domain.value_objects.membership_policy import MembershipPolicy
from tests.factories import AccentColorFactory, EmailFactory, IdFactory, InvitationTokenFactory


# ── Value Object фикстуры ─────────────────────────────────────────────────


@pytest.fixture
def any_accent_color() -> AccentColor:
    """Случайный AccentColor."""
    return AccentColorFactory()


@pytest.fixture
def any_org_id() -> Id:
    """Случайный org_id."""
    return IdFactory()


@pytest.fixture
def any_owner_id() -> Id:
    """Случайный owner_id."""
    return IdFactory()


@pytest.fixture
def any_role_id() -> Id:
    """Случайный role_id."""
    return IdFactory()


@pytest.fixture
def any_email() -> Email:
    """Случайный Email."""
    return EmailFactory()


@pytest.fixture
def any_url() -> Url:
    """URL по умолчанию."""
    return Url("https://example.com/icon.png")


# ── Агрегат Organization ──────────────────────────────────────────────────


@pytest.fixture
def new_organization(any_owner_id: Id) -> Organization:
    """Организация после создания."""
    return Organization.create(name="TestOrg", owner_id=any_owner_id)


@pytest.fixture
def organization(new_organization: Organization) -> Organization:
    """Организация с очищенными событиями (после создания)."""
    new_organization.clear_domain_events()
    return new_organization


@pytest.fixture
def suspended_organization(organization: Organization) -> Organization:
    """Приостановленная организация."""
    organization.suspend("test reason")
    organization.clear_domain_events()
    return organization


@pytest.fixture
def pending_deletion_organization(organization: Organization) -> Organization:
    """Организация в процессе удаления."""
    organization.request_deletion()
    organization.clear_domain_events()
    return organization


# ── Агрегат Team ──────────────────────────────────────────────────────────


@pytest.fixture
def new_team(any_org_id: Id) -> Team:
    """Команда после создания."""
    return Team.create(org_id=any_org_id, name="TestTeam")


@pytest.fixture
def team(new_team: Team) -> Team:
    """Команда с очищенными событиями (после создания)."""
    new_team.clear_domain_events()
    return new_team


@pytest.fixture
def team_with_lead(any_org_id: Id) -> Team:
    """Команда с лидером."""
    lead_id = IdFactory()
    return Team.create(org_id=any_org_id, name="TestTeam", lead_id=lead_id)


@pytest.fixture
def inactive_team(team: Team) -> Team:
    """Неактивная команда."""
    team.deactivate()
    team.clear_domain_events()
    return team


# ── Агрегат Invitation ────────────────────────────────────────────────────


@pytest.fixture
def email_invitation(any_org_id: Id, any_email: Email, any_role_id: Id, any_owner_id: Id) -> Invitation:
    """Email-приглашение."""
    return Invitation.create_email_invitation(
        org_id=any_org_id, email=any_email, role_id=any_role_id, invited_by=any_owner_id,
    )


@pytest.fixture
def link_invitation(any_org_id: Id, any_role_id: Id, any_owner_id: Id) -> Invitation:
    """Link-приглашение."""
    return Invitation.create_link_invitation(
        org_id=any_org_id, role_id=any_role_id, invited_by=any_owner_id, token_value="abc123",
    )


@pytest.fixture
def accepted_invitation(email_invitation: Invitation) -> Invitation:
    """Принятое приглашение."""
    user_id = IdFactory()
    email_invitation.accept(user_id)
    email_invitation.clear_domain_events()
    return email_invitation


# ── Агрегат OrgMembership ─────────────────────────────────────────────────


@pytest.fixture
def new_membership(any_org_id: Id, any_owner_id: Id, any_role_id: Id) -> OrgMembership:
    """Членство организации после создания."""
    return OrgMembership.create(org_id=any_org_id, owner_id=any_owner_id, owner_role_id=any_role_id)


@pytest.fixture
def membership(new_membership: OrgMembership) -> OrgMembership:
    """Членство с очищенными событиями (после создания)."""
    new_membership.clear_domain_events()
    return new_membership


# ── Агрегат OrgRole ───────────────────────────────────────────────────────


@pytest.fixture
def system_role() -> OrgRole:
    """Системная роль."""
    return OrgRole.create_system(
        name="owner", permissions=["*"], scope=OrgRoleScope.ORG, description="Owner role",
    )


@pytest.fixture
def custom_role(any_org_id: Id) -> OrgRole:
    """Кастомная роль."""
    return OrgRole.create_custom(
        org_id=any_org_id, name="custom_role", permissions=["read"], scope=OrgRoleScope.ORG,
    )


# ── Агрегат Department ────────────────────────────────────────────────────


@pytest.fixture
def new_department(any_org_id: Id) -> Department:
    """Подразделение после создания."""
    return Department.create(org_id=any_org_id, name="Engineering")


@pytest.fixture
def department(new_department: Department) -> Department:
    """Подразделение с очищенными событиями (после создания)."""
    new_department.clear_domain_events()
    return new_department


# ── Агрегат SSOIntegration ────────────────────────────────────────────────


@pytest.fixture
def new_sso(any_org_id: Id, any_owner_id: Id) -> SSOIntegration:
    """SSO-интеграция после создания."""
    return SSOIntegration.create(
        org_id=any_org_id,
        provider=SSOProvider.SAML,
        entity_id="https://idp.example.com",
        sso_url="https://idp.example.com/sso",
        certificate="MIIC...",
        added_by=any_owner_id,
    )


@pytest.fixture
def sso(new_sso: SSOIntegration) -> SSOIntegration:
    """SSO-интеграция с очищенными событиями (после создания)."""
    new_sso.clear_domain_events()
    return new_sso


# ── Агрегат StorageIntegration ────────────────────────────────────────────


@pytest.fixture
def new_storage(any_org_id: Id) -> StorageIntegration:
    """Хранилище организации после создания."""
    config = StorageConfig(provider=StorageProvider.LOCAL)
    quota = StorageQuota(max_bytes=1_000_000, used_bytes=0)
    return StorageIntegration.create(org_id=any_org_id, config=config, quota=quota)


@pytest.fixture
def storage(new_storage: StorageIntegration) -> StorageIntegration:
    """Хранилище с очищенными событиями (после создания)."""
    new_storage.clear_domain_events()
    return new_storage
