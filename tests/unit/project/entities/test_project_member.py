"""Unit-тесты для ProjectMember (Project BC)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.project.domain.entities.project_member import ProjectMember


@pytest.mark.unit
class TestProjectMember:
    def test_create(self) -> None:
        user_id = Id.generate()
        role_id = Id.generate()
        member = ProjectMember(user_id=user_id, role_id=role_id)
        assert member.user_id == user_id
        assert member.role_id == role_id
        assert member.id is not None
        assert member.is_active
        assert member.joined_at is not None

    def test_equality_by_id(self) -> None:
        shared_id = Id.generate()
        user_id = Id.generate()
        role_id = Id.generate()
        m1 = ProjectMember(id=shared_id, user_id=user_id, role_id=role_id)
        m2 = ProjectMember(id=shared_id, user_id=user_id, role_id=role_id)
        assert m1 == m2

    def test_inequality_different_id(self) -> None:
        m1 = ProjectMember(user_id=Id.generate(), role_id=Id.generate())
        m2 = ProjectMember(user_id=Id.generate(), role_id=Id.generate())
        assert m1 != m2
