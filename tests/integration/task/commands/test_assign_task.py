"""Интеграционные тесты AssignTaskHandler (реальные repos + стабы портов)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.task.application.commands.assign_task import AssignTaskCommand, AssignTaskHandler
from app.context.task.application.exceptions.authorization_exceptions import InsufficientTaskPermissionsException
from app.context.task.domain.exceptions.task_exceptions import TaskNotFoundException


@pytest.mark.integration
class TestAssignTaskHandler:
    """Тесты назначения исполнителя — full stack."""

    @pytest.fixture
    def handler(self, task_repo, changelog_repo, identity_user_stub, project_membership_stub, permission_checker_stub, event_bus_stub) -> AssignTaskHandler:
        return AssignTaskHandler(
            task_repo=task_repo,
            changelog_repo=changelog_repo,
            identity_port=identity_user_stub,
            membership_port=project_membership_stub,
            permission_checker=permission_checker_stub,
            event_bus=event_bus_stub,
        )

    async def test_assign_task_success(self, handler, task_repo, make_task) -> None:
        task = await make_task()
        assignee_id = Id.generate()
        changed_by = Id.generate()

        cmd = AssignTaskCommand(
            task_id=str(task.id),
            assignee_id=str(assignee_id),
            changed_by=str(changed_by),
        )
        await handler.handle(cmd)

        found = await task_repo.get_by_id(task.id)
        assert found is not None
        assert assignee_id in found.assignee_ids

    async def test_assign_task_creates_changelog(self, handler, changelog_repo, make_task) -> None:
        task = await make_task()
        assignee_id = Id.generate()

        cmd = AssignTaskCommand(
            task_id=str(task.id),
            assignee_id=str(assignee_id),
            changed_by=str(assignee_id),
        )
        await handler.handle(cmd)

        entries = await changelog_repo.get_by_task_and_field(task.id, "assignee")
        assert len(entries) >= 1

    async def test_assign_task_not_found(self, handler) -> None:
        cmd = AssignTaskCommand(
            task_id=str(Id.generate()),
            assignee_id=str(Id.generate()),
            changed_by=str(Id.generate()),
        )
        with pytest.raises(TaskNotFoundException):
            await handler.handle(cmd)

    async def test_assign_task_permission_denied(self, task_repo, changelog_repo, identity_user_stub, project_membership_stub, permission_denied_stub, event_bus_stub, make_task) -> None:
        task = await make_task()
        handler = AssignTaskHandler(
            task_repo=task_repo,
            changelog_repo=changelog_repo,
            identity_port=identity_user_stub,
            membership_port=project_membership_stub,
            permission_checker=permission_denied_stub,
            event_bus=event_bus_stub,
        )
        assignee_id = Id.generate()
        changed_by = Id.generate()
        cmd = AssignTaskCommand(
            task_id=str(task.id),
            assignee_id=str(assignee_id),
            changed_by=str(changed_by),
        )
        with pytest.raises(InsufficientTaskPermissionsException):
            await handler.handle(cmd)
