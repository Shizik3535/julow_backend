"""Интеграционные тесты GetDepartmentsByOrgHandler (реальные repos)."""

import pytest

from app.context.organization.application.dto.department_dto import DepartmentListDTO
from app.context.organization.application.queries.get_departments_by_org import (
    GetDepartmentsByOrgHandler,
    GetDepartmentsByOrgQuery,
)


@pytest.mark.integration
class TestGetDepartmentsByOrgHandler:
    @pytest.fixture
    def handler(self, department_repo) -> GetDepartmentsByOrgHandler:
        return GetDepartmentsByOrgHandler(department_repo=department_repo)

    async def test_returns_departments(self, handler, make_department, make_org) -> None:
        org = await make_org()
        dept = await make_department(org_id=org.id)
        query = GetDepartmentsByOrgQuery(org_id=str(org.id))
        result = await handler.handle(query)
        assert isinstance(result, DepartmentListDTO)
        assert any(d.id == str(dept.id) for d in result.items)

    async def test_empty_for_unknown_org(self, handler) -> None:
        from app.shared.domain.value_objects.id_vo import Id

        query = GetDepartmentsByOrgQuery(org_id=str(Id.generate()))
        result = await handler.handle(query)
        assert result.total == 0
