"""Unit-тесты для WorkspaceMember (Workspace BC)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.domain.entities.workspace_member import WorkspaceMember
from app.context.workspace.domain.value_objects.member_source import MemberSource


@pytest.mark.unit
class TestWorkspaceMember:
    def test_create_with_defaults(self) -> None:
        member = WorkspaceMember(user_id=Id.generate())
        assert member.is_active is True
        assert member.source == MemberSource.DIRECT
        assert member.display_name is None
        assert member.invited_by is None

    def test_create_with_custom_values(self) -> None:
        user_id = Id.generate()
        role_id = Id.generate()
        invited_by = Id.generate()
        member = WorkspaceMember(
            user_id=user_id,
            role_id=role_id,
            source=MemberSource.ORGANIZATION,
            display_name="Alice",
            invited_by=invited_by,
        )
        assert member.user_id == user_id
        assert member.role_id == role_id
        assert member.source == MemberSource.ORGANIZATION
        assert member.display_name == "Alice"
        assert member.invited_by == invited_by

    def test_equality_by_id(self) -> None:
        shared_id = Id.generate()
        user_id = Id.generate()
        role_id = Id.generate()
        m1 = WorkspaceMember(id=shared_id, user_id=user_id, role_id=role_id)
        m2 = WorkspaceMember(id=shared_id, user_id=user_id, role_id=role_id)
        assert m1 == m2

    def test_inequality_different_id(self) -> None:
        user_id = Id.generate()
        role_id = Id.generate()
        m1 = WorkspaceMember(user_id=user_id, role_id=role_id)
        m2 = WorkspaceMember(user_id=user_id, role_id=role_id)
        assert m1 != m2
