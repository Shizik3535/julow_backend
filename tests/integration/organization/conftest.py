"""
Organization BC conftest — фикстуры для integration-тестов Organization.

Предоставляет mappers, repositories, seed-хелперы и реальные порты.
"""

import uuid

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.domain.value_objects.email_vo import Email
from app.shared.domain.value_objects.id_vo import Id
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.context.organization.application.ports.authorization.org_permission_checker_port import (
    OrgPermissionCheckerPort,
)
from app.context.organization.application.ports.encryption.encryption_port import EncryptionPort
from app.context.organization.application.ports.integration.inboard.identity_user_port import IdentityUserPort

from app.context.identity.domain.aggregates.user import User
from app.context.identity.infrastructure.persistence.mappers.user_mapper import UserMapper
from app.context.identity.infrastructure.persistence.repositories.sql_user_repository import SqlUserRepository

from app.context.organization.domain.aggregates.department import Department
from app.context.organization.domain.aggregates.invitation import Invitation
from app.context.organization.domain.aggregates.org_membership import OrgMembership
from app.context.organization.domain.aggregates.org_role import OrgRole
from app.context.organization.domain.aggregates.organization import Organization
from app.context.organization.domain.aggregates.sso_integration import SSOIntegration
from app.context.organization.domain.aggregates.storage_integration import StorageIntegration
from app.context.organization.domain.aggregates.team import Team
from app.context.organization.domain.entities.org_member import OrgMember
from app.context.organization.domain.value_objects.invitation_token import InvitationToken
from app.context.organization.domain.value_objects.org_role_scope import OrgRoleScope
from app.context.organization.domain.value_objects.org_status import OrgStatus
from app.context.organization.domain.value_objects.sso_provider import SSOProvider
from app.context.organization.domain.value_objects.storage_config import StorageConfig
from app.context.organization.domain.value_objects.storage_provider import StorageProvider
from app.context.organization.domain.value_objects.storage_quota import StorageQuota

from app.context.organization.infrastructure.persistence.mappers.department_mapper import DepartmentMapper
from app.context.organization.infrastructure.persistence.mappers.invitation_mapper import InvitationMapper
from app.context.organization.infrastructure.persistence.mappers.org_membership_mapper import OrgMembershipMapper
from app.context.organization.infrastructure.persistence.mappers.org_role_mapper import OrgRoleMapper
from app.context.organization.infrastructure.persistence.mappers.organization_mapper import OrganizationMapper
from app.context.organization.infrastructure.persistence.mappers.sso_integration_mapper import SSOIntegrationMapper
from app.context.organization.infrastructure.persistence.mappers.storage_integration_mapper import (
    StorageIntegrationMapper,
)
from app.context.organization.infrastructure.persistence.mappers.team_mapper import TeamMapper

from app.context.organization.infrastructure.persistence.repositories.sql_department_repository import (
    SqlDepartmentRepository,
)
from app.context.organization.infrastructure.persistence.repositories.sql_invitation_repository import (
    SqlInvitationRepository,
)
from app.context.organization.infrastructure.persistence.repositories.sql_org_membership_repository import (
    SqlOrgMembershipRepository,
)
from app.context.organization.infrastructure.persistence.repositories.sql_org_role_repository import (
    SqlOrgRoleRepository,
)
from app.context.organization.infrastructure.persistence.repositories.sql_organization_repository import (
    SqlOrganizationRepository,
)
from app.context.organization.infrastructure.persistence.repositories.sql_sso_integration_repository import (
    SqlSSOIntegrationRepository,
)
from app.context.organization.infrastructure.persistence.repositories.sql_storage_integration_repository import (
    SqlStorageIntegrationRepository,
)
from app.context.organization.infrastructure.persistence.repositories.sql_team_repository import SqlTeamRepository

from app.context.organization.infrastructure.persistence.seed.org_roles import SYSTEM_ORG_ROLES


# ── Identity Mappers & Repos (FK-зависимость) ──────────────────────────────


@pytest.fixture
def user_mapper() -> UserMapper:
    return UserMapper()


@pytest.fixture
def user_repo(db_session: AsyncSession, user_mapper: UserMapper) -> SqlUserRepository:
    return SqlUserRepository(session=db_session, mapper=user_mapper)


# ── Organization Mappers ─────────────────────────────────────────────────────


@pytest.fixture
def organization_mapper() -> OrganizationMapper:
    return OrganizationMapper()


@pytest.fixture
def org_membership_mapper() -> OrgMembershipMapper:
    return OrgMembershipMapper()


@pytest.fixture
def org_role_mapper() -> OrgRoleMapper:
    return OrgRoleMapper()


@pytest.fixture
def department_mapper() -> DepartmentMapper:
    return DepartmentMapper()


@pytest.fixture
def team_mapper() -> TeamMapper:
    return TeamMapper()


@pytest.fixture
def invitation_mapper() -> InvitationMapper:
    return InvitationMapper()


@pytest.fixture
def sso_integration_mapper() -> SSOIntegrationMapper:
    return SSOIntegrationMapper()


@pytest.fixture
def storage_integration_mapper() -> StorageIntegrationMapper:
    return StorageIntegrationMapper()


# ── Organization Repositories ────────────────────────────────────────────────


@pytest.fixture
def org_repo(db_session: AsyncSession, organization_mapper: OrganizationMapper) -> SqlOrganizationRepository:
    return SqlOrganizationRepository(session=db_session, mapper=organization_mapper)


@pytest.fixture
def membership_repo(
    db_session: AsyncSession, org_membership_mapper: OrgMembershipMapper
) -> SqlOrgMembershipRepository:
    return SqlOrgMembershipRepository(session=db_session, mapper=org_membership_mapper)


@pytest.fixture
def org_role_repo(db_session: AsyncSession, org_role_mapper: OrgRoleMapper) -> SqlOrgRoleRepository:
    return SqlOrgRoleRepository(session=db_session, mapper=org_role_mapper)


@pytest.fixture
def department_repo(db_session: AsyncSession, department_mapper: DepartmentMapper) -> SqlDepartmentRepository:
    return SqlDepartmentRepository(session=db_session, mapper=department_mapper)


@pytest.fixture
def team_repo(db_session: AsyncSession, team_mapper: TeamMapper) -> SqlTeamRepository:
    return SqlTeamRepository(session=db_session, mapper=team_mapper)


@pytest.fixture
def invitation_repo(db_session: AsyncSession, invitation_mapper: InvitationMapper) -> SqlInvitationRepository:
    return SqlInvitationRepository(session=db_session, mapper=invitation_mapper)


@pytest.fixture
def sso_repo(
    db_session: AsyncSession, sso_integration_mapper: SSOIntegrationMapper
) -> SqlSSOIntegrationRepository:
    return SqlSSOIntegrationRepository(session=db_session, mapper=sso_integration_mapper)


@pytest.fixture
def storage_repo(
    db_session: AsyncSession, storage_integration_mapper: StorageIntegrationMapper
) -> SqlStorageIntegrationRepository:
    return SqlStorageIntegrationRepository(session=db_session, mapper=storage_integration_mapper)


# ── Seed Helpers ─────────────────────────────────────────────────────────────


@pytest.fixture
def _ensure_user(user_repo: SqlUserRepository):
    """Хелпер: гарантирует наличие User в БД для FK-зависимостей."""
    _created: set[Id] = set()

    async def _fn(user_id: Id | None = None) -> User:
        uid = user_id or Id.generate()
        found = await user_repo.get_by_id(uid)
        if found is not None:
            _created.add(uid)
            return found
        email_vo = Email(f"auto-org-{uuid.uuid4().hex[:8]}@test.com")
        user = User(id=uid, email=email_vo)
        user.clear_domain_events()
        await user_repo.add(user)
        _created.add(uid)
        return user

    return _fn


@pytest.fixture
def make_user(user_repo: SqlUserRepository, _ensure_user):
    """Фабрика: создаёт User и сохраняет в БД."""

    async def _make(
        email: str | None = None,
    ) -> User:
        email_vo = Email(email or f"org-user-{uuid.uuid4().hex[:8]}@test.com")
        user = User(id=Id.generate(), email=email_vo)
        user.clear_domain_events()
        await user_repo.add(user)
        return user

    return _make


@pytest.fixture
def make_org(org_repo: SqlOrganizationRepository, _ensure_user):
    """Фабрика: создаёт Organization с владельцем и сохраняет в БД."""

    async def _make(
        name: str | None = None,
        owner_id: Id | None = None,
    ) -> Organization:
        oid = owner_id or Id.generate()
        await _ensure_user(oid)
        org_name = name or f"org-{uuid.uuid4().hex[:6]}"
        org = Organization.create(name=org_name, owner_id=oid)
        org.clear_domain_events()
        await org_repo.add(org)
        return org

    return _make


@pytest.fixture
def make_org_with_membership(
    org_repo: SqlOrganizationRepository,
    membership_repo: SqlOrgMembershipRepository,
    org_role_repo: SqlOrgRoleRepository,
    _ensure_user,
):
    """
    Фабрика: создаёт Organization + 4 системных OrgRole + OrgMembership
    с владельцем как первым участником с ролью owner.
    """

    async def _make(
        name: str | None = None,
        owner_id: Id | None = None,
    ) -> dict:
        oid = owner_id or Id.generate()
        await _ensure_user(oid)
        org_name = name or f"org-{uuid.uuid4().hex[:6]}"

        org = Organization.create(name=org_name, owner_id=oid)
        org.clear_domain_events()
        await org_repo.add(org)

        owner_role: OrgRole | None = None
        for seed_role in SYSTEM_ORG_ROLES:
            role = OrgRole.create_custom(
                org_id=org.id,
                name=seed_role["name"],
                permissions=seed_role["permissions"],
                scope=OrgRoleScope(seed_role["scope"]),
                description=seed_role["description"],
            )
            role.is_system = True
            role.clear_domain_events()
            await org_role_repo.add(role)
            if seed_role["name"] == "owner":
                owner_role = role

        membership = OrgMembership.create(
            org_id=org.id,
            owner_id=oid,
            owner_role_id=owner_role.id if owner_role else Id.generate(),
        )
        membership.clear_domain_events()
        await membership_repo.add(membership)

        return {
            "org": org,
            "membership": membership,
            "owner_role": owner_role,
            "owner_id": oid,
        }

    return _make


@pytest.fixture
def make_org_role(org_role_repo: SqlOrgRoleRepository, make_org):
    """Фабрика: создаёт кастомную OrgRole и сохраняет в БД."""

    async def _make(
        org_id: Id | None = None,
        name: str | None = None,
        permissions: list[str] | None = None,
        scope: OrgRoleScope = OrgRoleScope.ORG,
        description: str | None = None,
    ) -> OrgRole:
        if org_id is None:
            org = await make_org()
            org_id = org.id
        role_name = name or f"custom-role-{uuid.uuid4().hex[:6]}"
        role = OrgRole.create_custom(
            org_id=org_id,
            name=role_name,
            permissions=permissions or ["org.read"],
            scope=scope,
            description=description,
        )
        role.clear_domain_events()
        await org_role_repo.add(role)
        return role

    return _make


@pytest.fixture
def make_department(department_repo: SqlDepartmentRepository, make_org):
    """Фабрика: создаёт Department и сохраняет в БД."""

    async def _make(
        org_id: Id | None = None,
        name: str | None = None,
        parent_id: Id | None = None,
        lead_id: Id | None = None,
    ) -> Department:
        if org_id is None:
            org = await make_org()
            org_id = org.id
        dept_name = name or f"dept-{uuid.uuid4().hex[:6]}"
        dept = Department.create(org_id=org_id, name=dept_name, parent_id=parent_id, lead_id=lead_id)
        dept.clear_domain_events()
        await department_repo.add(dept)
        return dept

    return _make


@pytest.fixture
def make_team(team_repo: SqlTeamRepository, make_org):
    """Фабрика: создаёт Team и сохраняет в БД."""

    async def _make(
        org_id: Id | None = None,
        name: str | None = None,
        lead_id: Id | None = None,
    ) -> Team:
        if org_id is None:
            org = await make_org()
            org_id = org.id
        team_name = name or f"team-{uuid.uuid4().hex[:6]}"
        team = Team.create(org_id=org_id, name=team_name, lead_id=lead_id)
        team.clear_domain_events()
        await team_repo.add(team)
        return team

    return _make


@pytest.fixture
def make_invitation(invitation_repo: SqlInvitationRepository, make_org):
    """Фабрика: создаёт email-приглашение и сохраняет в БД."""

    async def _make(
        org_id: Id | None = None,
        email: str | None = None,
        role_id: Id | None = None,
        invited_by: Id | None = None,
    ) -> Invitation:
        if org_id is None:
            org = await make_org()
            org_id = org.id
        email_vo = Email(email or f"invite-{uuid.uuid4().hex[:8]}@test.com")
        inv = Invitation.create_email_invitation(
            org_id=org_id,
            email=email_vo,
            role_id=role_id or Id.generate(),
            invited_by=invited_by or Id.generate(),
        )
        inv.clear_domain_events()
        await invitation_repo.add(inv)
        return inv

    return _make


@pytest.fixture
def make_link_invitation(invitation_repo: SqlInvitationRepository, make_org):
    """Фабрика: создаёт link-приглашение и сохраняет в БД."""

    async def _make(
        org_id: Id | None = None,
        role_id: Id | None = None,
        invited_by: Id | None = None,
        token_value: str | None = None,
    ) -> Invitation:
        if org_id is None:
            org = await make_org()
            org_id = org.id
        token = token_value or f"link-{uuid.uuid4().hex[:12]}"
        inv = Invitation.create_link_invitation(
            org_id=org_id,
            role_id=role_id or Id.generate(),
            invited_by=invited_by or Id.generate(),
            token_value=token,
        )
        inv.clear_domain_events()
        await invitation_repo.add(inv)
        return inv

    return _make


@pytest.fixture
def make_sso_integration(sso_repo: SqlSSOIntegrationRepository, make_org, _ensure_user):
    """Фабрика: создаёт SSO-интеграцию и сохраняет в БД."""

    async def _make(
        org_id: Id | None = None,
        provider: SSOProvider = SSOProvider.SAML,
        added_by: Id | None = None,
    ) -> SSOIntegration:
        if org_id is None:
            org = await make_org()
            org_id = org.id
        if added_by is None:
            added_by = Id.generate()
            await _ensure_user(added_by)
        integration = SSOIntegration.create(
            org_id=org_id,
            provider=provider,
            entity_id=f"entity-{uuid.uuid4().hex[:8]}",
            sso_url=f"https://sso.example.com/{uuid.uuid4().hex[:8]}",
            certificate=f"cert-{uuid.uuid4().hex[:8]}",
            added_by=added_by,
        )
        integration.clear_domain_events()
        await sso_repo.add(integration)
        return integration

    return _make


@pytest.fixture
def make_storage_integration(storage_repo: SqlStorageIntegrationRepository, make_org):
    """Фабрика: создаёт StorageIntegration и сохраняет в БД."""

    async def _make(
        org_id: Id | None = None,
        config: StorageConfig | None = None,
        quota: StorageQuota | None = None,
    ) -> StorageIntegration:
        if org_id is None:
            org = await make_org()
            org_id = org.id
        storage_config = config or StorageConfig(provider=StorageProvider.LOCAL)
        storage_quota = quota or StorageQuota(max_bytes=0, used_bytes=0)
        storage = StorageIntegration.create(
            org_id=org_id,
            config=storage_config,
            quota=storage_quota,
        )
        storage.clear_domain_events()
        await storage_repo.add(storage)
        return storage

    return _make


# ── Stubs for Command Handler Tests ─────────────────────────────────────────


class _AlwaysAllowPermissionChecker(OrgPermissionCheckerPort):
    """Stub: всегда разрешает любые действия."""

    async def has_permission(self, user_id: Id, org_id: Id, permission: str) -> bool:
        return True

    async def require_permission(self, user_id: Id, org_id: Id, permission: str) -> None:
        pass


class _NoopEventBus(DomainEventBus):
    """Stub: поглощает все события без публикации."""

    async def publish_all(self, events: list) -> None:
        pass

    async def publish(self, event) -> None:
        pass


class _StubEncryptionPort(EncryptionPort):
    """Stub: «шифрует» добавлением префикса, «расшифровывает» убирая его."""

    PREFIX = "enc:"

    async def encrypt(self, plaintext: str) -> str:
        return f"{self.PREFIX}{plaintext}"

    async def decrypt(self, ciphertext: str) -> str:
        return ciphertext.removeprefix(self.PREFIX)


class _StubIdentityUserPort(IdentityUserPort):
    """Stub: считает, что все пользователи существуют."""

    async def user_exists(self, user_id: str) -> bool:
        return True

    async def get_user(self, user_id: str) -> dict | None:
        return {"id": user_id, "email": f"stub-{user_id}@test.com"}


@pytest.fixture
def permission_checker_stub() -> _AlwaysAllowPermissionChecker:
    return _AlwaysAllowPermissionChecker()


@pytest.fixture
def event_bus_stub() -> _NoopEventBus:
    return _NoopEventBus()


@pytest.fixture
def encryption_stub() -> _StubEncryptionPort:
    return _StubEncryptionPort()


@pytest.fixture
def identity_user_stub() -> _StubIdentityUserPort:
    return _StubIdentityUserPort()
