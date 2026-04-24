"""Интеграционные тесты RemoveDepartmentMemberHandler (реальные repos + stubs)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.application.commands.remove_department_member import (
    RemoveDepartmentMemberCommand,
    RemoveDepartmentMemberHandler,
)


@pytest.mark.integration
class TestRemoveDepartmentMemberHandler:
    @pytest.fixture
    def handler(self, department_repo, permission_checker_stub, event_bus_stub):
        return RemoveDepartmentMemberHandler(
            department_repo=department_repo,
            org_permission_checker=permission_checker_stub,
            event_bus=event_bus_stub,
        )

    async def test_remove_member(self, handler, make_org_with_membership, make_department, department_repo) -> None:
        data = await make_org_with_membership()
        dept = await make_department(org_id=data["org"].id)
        dept.add_member(data["owner_id"])
        dept.clear_domain_events()
        await department_repo.update(dept)

        cmd = RemoveDepartmentMemberCommand(
            caller_id=str(Id.generate()),
            org_id=str(data["org"].id),
            department_id=str(dept.id),
            user_id=str(data["owner_id"]),
        )
        await handler.handle(cmd)
        found = await department_repo.get_by_id(dept.id)
        assert found is not None
        assert data["owner_id"] not in found.member_ids
