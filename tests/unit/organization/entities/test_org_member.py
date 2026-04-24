"""Unit-тесты для OrgMember (Organization BC)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.domain.entities.org_member import OrgMember


@pytest.mark.unit
class TestOrgMember:
    def test_create(self) -> None:
        user_id = Id.generate()
        role_id = Id.generate()
        member = OrgMember(user_id=user_id, role_id=role_id)
        assert member.user_id == user_id
        assert member.role_id == role_id
        assert member.is_active is True
        assert member.display_name is None
        assert member.invited_by is None

    def test_create_with_display_name(self) -> None:
        member = OrgMember(
            user_id=Id.generate(),
            role_id=Id.generate(),
            display_name="John",
            invited_by=Id.generate(),
        )
        assert member.display_name == "John"
        assert member.invited_by is not None

    def test_equality_by_id_and_fields(self) -> None:
        shared_id = Id.generate()
        user_id = Id.generate()
        role_id = Id.generate()
        m1 = OrgMember(id=shared_id, user_id=user_id, role_id=role_id)
        m2 = OrgMember(id=shared_id, user_id=user_id, role_id=role_id)
        assert m1 == m2

    def test_inequality_different_id(self) -> None:
        m1 = OrgMember(user_id=Id.generate(), role_id=Id.generate())
        m2 = OrgMember(user_id=Id.generate(), role_id=Id.generate())
        assert m1 != m2

    def test_inequality_same_id_different_fields(self) -> None:
        shared_id = Id.generate()
        m1 = OrgMember(id=shared_id, user_id=Id.generate(), role_id=Id.generate())
        m2 = OrgMember(id=shared_id, user_id=Id.generate(), role_id=Id.generate())
        assert m1 != m2
