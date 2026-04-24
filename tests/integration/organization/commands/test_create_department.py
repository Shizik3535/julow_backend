"""Интеграционные тесты CreateDepartmentHandler (реальные repos + stubs)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.application.commands.create_department import (
    CreateDepartmentCommand,
    CreateDepartmentHandler,
)
from app.context.organization.application.dto.department_dto import DepartmentDTO


@pytest.mark.integration
class TestCreateDepartmentHandler:
    @pytest.fixture
    def handler(self, department_repo, permission_checker_stub, event_bus_stub):
        return CreateDepartmentHandler(
            department_repo=department_repo,
            org_permission_checker=permission_checker_stub,
            event_bus=event_bus_stub,
        )

    async def test_create_department(self, handler, make_org) -> None:
        org = await make_org()
        cmd = CreateDepartmentCommand(
            caller_id=str(Id.generate()),
            org_id=str(org.id),
            name="Engineering",
        )
        result = await handler.handle(cmd)
        assert isinstance(result, DepartmentDTO)
        assert result.name == "Engineering"

    async def test_create_with_parent(self, handler, make_org, make_department) -> None:
        org = await make_org()
        parent = await make_department(org_id=org.id)
        cmd = CreateDepartmentCommand(
            caller_id=str(Id.generate()),
            org_id=str(org.id),
            name="Backend",
            parent_id=str(parent.id),
        )
        result = await handler.handle(cmd)
        assert result.parent_id == str(parent.id)
