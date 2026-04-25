"""Интеграционные тесты WorkspacePermissionCheckerAdapter (реальные repos)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.project.infrastructure.integration.inboard.workspace_permission_checker_adapter import (
    WorkspacePermissionCheckerAdapter,
)
from app.context.project.application.exceptions.authorization_exceptions import (
    InsufficientProjectPermissionsException,
)


class _StubWorkspaceMembershipProvider:
    """Stub WorkspaceMembershipProvider для тестов."""

    def __init__(self, is_member: bool = True, has_permission: bool = True):
        self._is_member = is_member
        self._has_permission = has_permission

    async def is_member(self, workspace_id: str, user_id: str) -> bool:
        return self._is_member

    async def has_permission(self, user_id: str, workspace_id: str, permission: str) -> bool:
        return self._has_permission


@pytest.mark.integration
class TestWorkspacePermissionCheckerAdapter:
    """Тесты WorkspacePermissionCheckerAdapter — inboard adapter."""

    async def test_require_permission_allowed(self) -> None:
        provider = _StubWorkspaceMembershipProvider(is_member=True, has_permission=True)
        adapter = WorkspacePermissionCheckerAdapter(workspace_membership_provider=provider)
        # Should not raise
        await adapter.require_permission(
            user_id=str(Id.generate()),
            workspace_id=str(Id.generate()),
            permission="projects.create",
        )

    async def test_require_permission_denied(self) -> None:
        provider = _StubWorkspaceMembershipProvider(is_member=True, has_permission=False)
        adapter = WorkspacePermissionCheckerAdapter(workspace_membership_provider=provider)
        with pytest.raises(InsufficientProjectPermissionsException):
            await adapter.require_permission(
                user_id=str(Id.generate()),
                workspace_id=str(Id.generate()),
                permission="projects.create",
            )

    async def test_has_permission_returns_true(self) -> None:
        provider = _StubWorkspaceMembershipProvider(has_permission=True)
        adapter = WorkspacePermissionCheckerAdapter(workspace_membership_provider=provider)
        result = await adapter.has_permission(
            user_id=str(Id.generate()),
            workspace_id=str(Id.generate()),
            permission="projects.create",
        )
        assert result is True

    async def test_has_permission_returns_false(self) -> None:
        provider = _StubWorkspaceMembershipProvider(has_permission=False)
        adapter = WorkspacePermissionCheckerAdapter(workspace_membership_provider=provider)
        result = await adapter.has_permission(
            user_id=str(Id.generate()),
            workspace_id=str(Id.generate()),
            permission="projects.create",
        )
        assert result is False
