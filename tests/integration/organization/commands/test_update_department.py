"""Интеграционные тесты UpdateDepartmentHandler (реальные repos + stubs)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.application.commands.update_department import (
    UpdateDepartmentCommand,
    UpdateDepartmentHandler,
)


@pytest.mark.integration
class TestUpdateDepartmentHandler:
    @pytest.fixture
    def handler(self, department_repo, permission_checker_stub, event_bus_stub):
        return UpdateDepartmentHandler(
            department_repo=department_repo,
            org_permission_checker=permission_checker_stub,
            event_bus=event_bus_stub,
        )

    async def test_update_name(self, handler, make_department, department_repo) -> None:
        dept = await make_department()
        cmd = UpdateDepartmentCommand(
            caller_id=str(Id.generate()),
            org_id=str(dept.org_id),
            department_id=str(dept.id),
            name="UpdatedDept",
        )
        await handler.handle(cmd)
        found = await department_repo.get_by_id(dept.id)
        assert found is not None
        assert found.name == "UpdatedDept"

    async def test_update_lead(self, handler, make_department, department_repo) -> None:
        new_lead = Id.generate()
        dept = await make_department()
        cmd = UpdateDepartmentCommand(
            caller_id=str(Id.generate()),
            org_id=str(dept.org_id),
            department_id=str(dept.id),
            lead_id=str(new_lead),
        )
        await handler.handle(cmd)
        found = await department_repo.get_by_id(dept.id)
        assert found is not None
        assert found.lead_id == new_lead
