"""Интеграционные тесты GetWorkspacesByOrganizationHandler."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.application.queries.get_workspaces_by_organization import (
    GetWorkspacesByOrganizationQuery,
    GetWorkspacesByOrganizationHandler,
)
from app.context.workspace.application.exceptions.authorization_exceptions import (
    InsufficientWorkspacePermissionsException,
)
from tests.integration.workspace.conftest import (
    _AlwaysAllowOrgPermissionChecker,
    _NoopEventBus,
)


class _StubOrgMembershipPort:
    """Stub: все пользователи — члены организации."""

    async def is_org_member(self, org_id: str, user_id: str) -> bool:
        return True

    async def get_org_members(self, org_id: str) -> list[dict]:
        return []

    async def org_exists(self, org_id: str) -> bool:
        return True


class _DenyOrgMembershipPort:
    """Stub: никто не является членом организации."""

    async def is_org_member(self, org_id: str, user_id: str) -> bool:
        return False

    async def get_org_members(self, org_id: str) -> list[dict]:
        return []

    async def org_exists(self, org_id: str) -> bool:
        return True


@pytest.mark.integration
class TestGetWorkspacesByOrganizationHandler:
    """Тесты GetWorkspacesByOrganizationHandler."""

    @pytest.fixture
    def handler(self, ws_repo) -> GetWorkspacesByOrganizationHandler:
        return GetWorkspacesByOrganizationHandler(
            ws_repo=ws_repo,
            org_membership_port=_StubOrgMembershipPort(),
            org_permission_checker=_AlwaysAllowOrgPermissionChecker(),
        )

    async def test_get_by_org_found(self, handler, make_workspace) -> None:
        org_id = Id.generate()
        ws = await make_workspace(organization_id=org_id, name="Org WS")
        query = GetWorkspacesByOrganizationQuery(
            caller_id=str(Id.generate()), organization_id=str(org_id),
        )
        result = await handler.handle(query)

        assert result.total >= 1
        assert any(w.name == "Org WS" for w in result.items)

    async def test_get_by_org_not_member(self, ws_repo) -> None:
        handler = GetWorkspacesByOrganizationHandler(
            ws_repo=ws_repo,
            org_membership_port=_DenyOrgMembershipPort(),
            org_permission_checker=_AlwaysAllowOrgPermissionChecker(),
        )
        query = GetWorkspacesByOrganizationQuery(
            caller_id=str(Id.generate()), organization_id=str(Id.generate()),
        )
        with pytest.raises(InsufficientWorkspacePermissionsException):
            await handler.handle(query)

    async def test_get_by_org_empty(self, handler) -> None:
        query = GetWorkspacesByOrganizationQuery(
            caller_id=str(Id.generate()), organization_id=str(Id.generate()),
        )
        result = await handler.handle(query)

        assert result.total == 0
