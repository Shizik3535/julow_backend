"""Интеграционные тесты WorkspaceMembershipAdapter (реальные repos)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.project.infrastructure.integration.inboard.workspace_membership_adapter import (
    WorkspaceMembershipAdapter,
)


class _StubWorkspaceMembershipProvider:
    """Stub WorkspaceMembershipProvider для тестов."""

    def __init__(self, is_member: bool = True):
        self._is_member = is_member

    async def is_member(self, workspace_id: str, user_id: str) -> bool:
        return self._is_member


@pytest.mark.integration
class TestWorkspaceMembershipAdapter:
    """Тесты WorkspaceMembershipAdapter — inboard adapter."""

    async def test_is_workspace_member_true(self) -> None:
        provider = _StubWorkspaceMembershipProvider(is_member=True)
        adapter = WorkspaceMembershipAdapter(workspace_membership_provider=provider)
        result = await adapter.is_workspace_member(str(Id.generate()), str(Id.generate()))
        assert result is True

    async def test_is_workspace_member_false(self) -> None:
        provider = _StubWorkspaceMembershipProvider(is_member=False)
        adapter = WorkspaceMembershipAdapter(workspace_membership_provider=provider)
        result = await adapter.is_workspace_member(str(Id.generate()), str(Id.generate()))
        assert result is False
