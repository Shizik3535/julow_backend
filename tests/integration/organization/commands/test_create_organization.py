"""Интеграционные тесты CreateOrganizationHandler (реальные repos + stubs)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.application.commands.create_organization import (
    CreateOrganizationCommand,
    CreateOrganizationHandler,
)
from app.context.organization.application.dto.organization_dto import OrganizationDTO
from app.context.organization.application.exceptions.membership_app_exceptions import UserNotFoundException


@pytest.mark.integration
class TestCreateOrganizationHandler:
    @pytest.fixture
    def handler(self, org_repo, membership_repo, org_role_repo, identity_user_stub, event_bus_stub):
        return CreateOrganizationHandler(
            org_repo=org_repo,
            membership_repo=membership_repo,
            org_role_repo=org_role_repo,
            identity_port=identity_user_stub,
            event_bus=event_bus_stub,
        )

    async def test_creates_org_with_roles_and_membership(
        self, handler, make_user
    ) -> None:
        user = await make_user()
        cmd = CreateOrganizationCommand(name="TestOrg", owner_id=str(user.id))
        result = await handler.handle(cmd)
        assert isinstance(result, OrganizationDTO)
        assert result.name == "TestOrg"
        assert str(user.id) in result.owner_ids

    async def test_creates_4_system_roles(
        self, handler, make_user, org_role_repo
    ) -> None:
        user = await make_user()
        cmd = CreateOrganizationCommand(name="RoleOrg", owner_id=str(user.id))
        result = await handler.handle(cmd)
        org_id = Id.from_string(result.id)
        roles = await org_role_repo.get_by_org(org_id)
        assert len(roles) >= 4

    async def test_user_not_found_raises(self, handler) -> None:
        from app.context.organization.application.ports.integration.inboard.identity_user_port import IdentityUserPort

        class _DenyIdentity(IdentityUserPort):
            async def user_exists(self, user_id: str) -> bool:
                return False

            async def get_user(self, user_id: str) -> dict | None:
                return None

        handler._identity_port = _DenyIdentity()
        cmd = CreateOrganizationCommand(name="NoUser", owner_id=str(Id.generate()))
        with pytest.raises(UserNotFoundException):
            await handler.handle(cmd)
