"""Интеграционные тесты GetDepartmentHandler (реальные repos)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.shared.domain.exceptions import EntityNotFoundException
from app.context.organization.application.dto.department_dto import DepartmentDTO
from app.context.organization.application.queries.get_department import (
    GetDepartmentHandler,
    GetDepartmentQuery,
)


@pytest.mark.integration
class TestGetDepartmentHandler:
    @pytest.fixture
    def handler(self, department_repo, permission_checker_stub) -> GetDepartmentHandler:
        return GetDepartmentHandler(department_repo=department_repo, org_permission_checker=permission_checker_stub)

    async def test_returns_department_dto(self, handler, make_department) -> None:
        dept = await make_department(name="Engineering")
        query = GetDepartmentQuery(caller_id=str(Id.generate()), org_id=str(dept.org_id), department_id=str(dept.id))
        result = await handler.handle(query)
        assert isinstance(result, DepartmentDTO)
        assert result.name == "Engineering"

    async def test_not_found_raises(self, handler) -> None:
        query = GetDepartmentQuery(caller_id=str(Id.generate()), org_id=str(Id.generate()), department_id=str(Id.generate()))
        with pytest.raises(EntityNotFoundException):
            await handler.handle(query)
