"""Интеграционные тесты DeleteDepartmentHandler (реальные repos + stubs)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.application.commands.delete_department import (
    DeleteDepartmentCommand,
    DeleteDepartmentHandler,
)


@pytest.mark.integration
class TestDeleteDepartmentHandler:
    @pytest.fixture
    def handler(self, department_repo, permission_checker_stub, event_bus_stub):
        return DeleteDepartmentHandler(
            department_repo=department_repo,
            org_permission_checker=permission_checker_stub,
            event_bus=event_bus_stub,
        )

    async def test_deactivate_department(self, handler, make_department, department_repo) -> None:
        dept = await make_department()
        cmd = DeleteDepartmentCommand(
            caller_id=str(Id.generate()),
            org_id=str(dept.org_id),
            department_id=str(dept.id),
        )
        await handler.handle(cmd)
        found = await department_repo.get_by_id(dept.id)
        assert found is not None
        assert found.is_active is False
