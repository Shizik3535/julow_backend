"""Unit-тесты для Role."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.identity.domain.aggregates.role import Role


@pytest.mark.unit
class TestRole:
    def test_create_system_role(self) -> None:
        role = Role(name="admin", permissions=["read", "write"], is_system=True, description="Administrator")
        assert role.name == "admin"
        assert role.is_system is True
        assert "read" in role.permissions

    def test_create_custom_role(self) -> None:
        role = Role(name="moderator", permissions=["read"], is_system=False)
        assert not role.is_system

    def test_equality_by_id(self) -> None:
        shared_id = Id.generate()
        r1 = Role(id=shared_id, name="admin")
        r2 = Role(id=shared_id, name="admin")
        assert r1 == r2

    def test_inequality_different_id(self) -> None:
        r1 = Role(name="admin")
        r2 = Role(name="admin")
        assert r1 != r2
