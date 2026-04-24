"""Интеграционные тесты AddDepartmentMemberHandler (реальные repos + stubs)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.application.commands.add_department_member import (
    AddDepartmentMemberCommand,
    AddDepartmentMemberHandler,
)
from app.context.organization.application.exceptions.membership_app_exceptions import (
    MemberNotInOrganizationException,
)


@pytest.mark.integration
class TestAddDepartmentMemberHandler:
    @pytest.fixture
    def handler(self, department_repo, membership_repo, permission_checker_stub, event_bus_stub):
        return AddDepartmentMemberHandler(
            department_repo=department_repo,
            membership_repo=membership_repo,
            org_permission_checker=permission_checker_stub,
            event_bus=event_bus_stub,
        )

    async def test_add_member(self, handler, make_org_with_membership, make_department, department_repo) -> None:
        data = await make_org_with_membership()
        dept = await make_department(org_id=data["org"].id)

        cmd = AddDepartmentMemberCommand(
            caller_id=str(Id.generate()),
            org_id=str(data["org"].id),
            department_id=str(dept.id),
            user_id=str(data["owner_id"]),
        )
        await handler.handle(cmd)
        found = await department_repo.get_by_id(dept.id)
        assert found is not None
        assert data["owner_id"] in found.member_ids

    async def test_non_member_raises(self, handler, make_org, make_department) -> None:
        org = await make_org()
        dept = await make_department(org_id=org.id)
        non_member = Id.generate()

        cmd = AddDepartmentMemberCommand(
            caller_id=str(Id.generate()),
            org_id=str(org.id),
            department_id=str(dept.id),
            user_id=str(non_member),
        )
        with pytest.raises(MemberNotInOrganizationException):
            await handler.handle(cmd)
