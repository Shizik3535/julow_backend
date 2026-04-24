"""Интеграционные тесты SqlDepartmentRepository (реальная PostgreSQL)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.domain.aggregates.department import Department
from app.context.organization.infrastructure.persistence.repositories.sql_department_repository import (
    SqlDepartmentRepository,
)


@pytest.mark.integration
class TestSqlDepartmentRepositoryAdd:
    """Тесты добавления."""

    async def test_add_and_get_by_id(self, department_repo: SqlDepartmentRepository, make_department) -> None:
        dept = await make_department(name="Engineering")
        found = await department_repo.get_by_id(dept.id)
        assert found is not None
        assert found.id == dept.id

    async def test_add_persists_member_ids(
        self, department_repo: SqlDepartmentRepository, make_department, _ensure_user
    ) -> None:
        user_id = Id.generate()
        await _ensure_user(user_id)
        dept = await make_department()
        dept.add_member(user_id)
        dept.clear_domain_events()
        await department_repo.update(dept)

        found = await department_repo.get_by_id(dept.id)
        assert found is not None
        assert user_id in found.member_ids


@pytest.mark.integration
class TestSqlDepartmentRepositorySearch:
    """Тесты поиска."""

    async def test_get_by_org_id(self, department_repo: SqlDepartmentRepository, make_department, make_org) -> None:
        org = await make_org()
        dept = await make_department(org_id=org.id)
        found = await department_repo.get_by_org_id(org.id)
        assert len(found) >= 1
        assert any(d.id == dept.id for d in found)

    async def test_get_by_parent(self, department_repo: SqlDepartmentRepository, make_department) -> None:
        parent = await make_department(name="Parent")
        child = await make_department(parent_id=parent.id, name="Child")
        found = await department_repo.get_by_parent(parent.id)
        assert len(found) >= 1
        assert any(d.id == child.id for d in found)

    async def test_get_by_member(
        self, department_repo: SqlDepartmentRepository, make_department, _ensure_user
    ) -> None:
        user_id = Id.generate()
        await _ensure_user(user_id)
        dept = await make_department()
        dept.add_member(user_id)
        dept.clear_domain_events()
        await department_repo.update(dept)

        found = await department_repo.get_by_member(user_id)
        assert len(found) >= 1
        assert any(d.id == dept.id for d in found)


@pytest.mark.integration
class TestSqlDepartmentRepositoryUpdate:
    """Тесты обновления."""

    async def test_update_name(self, department_repo: SqlDepartmentRepository, make_department) -> None:
        dept = await make_department()
        dept.update(name="UpdatedDept")
        dept.clear_domain_events()
        await department_repo.update(dept)

        found = await department_repo.get_by_id(dept.id)
        assert found is not None
        assert found.name == "UpdatedDept"

    async def test_update_lead_id(self, department_repo: SqlDepartmentRepository, make_department) -> None:
        new_lead = Id.generate()
        dept = await make_department()
        dept.update(lead_id=new_lead)
        dept.clear_domain_events()
        await department_repo.update(dept)

        found = await department_repo.get_by_id(dept.id)
        assert found is not None
        assert found.lead_id == new_lead

    async def test_update_add_member(
        self, department_repo: SqlDepartmentRepository, make_department, _ensure_user
    ) -> None:
        user_id = Id.generate()
        await _ensure_user(user_id)
        dept = await make_department()
        dept.add_member(user_id)
        dept.clear_domain_events()
        await department_repo.update(dept)

        found = await department_repo.get_by_id(dept.id)
        assert found is not None
        assert user_id in found.member_ids

    async def test_update_remove_member(
        self, department_repo: SqlDepartmentRepository, make_department, _ensure_user
    ) -> None:
        user_id = Id.generate()
        await _ensure_user(user_id)
        dept = await make_department()
        dept.add_member(user_id)
        dept.clear_domain_events()
        await department_repo.update(dept)

        dept.remove_member(user_id)
        dept.clear_domain_events()
        await department_repo.update(dept)

        found = await department_repo.get_by_id(dept.id)
        assert found is not None
        assert user_id not in found.member_ids

    async def test_update_deactivate(self, department_repo: SqlDepartmentRepository, make_department) -> None:
        dept = await make_department()
        dept.deactivate()
        dept.clear_domain_events()
        await department_repo.update(dept)

        found = await department_repo.get_by_id(dept.id)
        assert found is not None
        assert found.is_active is False


@pytest.mark.integration
class TestSqlDepartmentRepositoryDelete:
    """Тесты удаления."""

    async def test_delete(self, department_repo: SqlDepartmentRepository, make_department) -> None:
        dept = await make_department()
        await department_repo.delete(dept.id)
        found = await department_repo.get_by_id(dept.id)
        assert found is None
