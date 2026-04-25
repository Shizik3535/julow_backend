"""Интеграционные тесты RemoveTaskFromSprintHandler (реальные repos + стабы портов)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.task.application.commands.remove_task_from_sprint import RemoveTaskFromSprintCommand, RemoveTaskFromSprintHandler
from app.context.task.application.exceptions.authorization_exceptions import InsufficientTaskPermissionsException
from app.context.task.domain.exceptions.task_exceptions import TaskNotFoundException


@pytest.mark.integration
class TestRemoveTaskFromSprintHandler:
    """Тесты убирания задачи из спринта — full stack."""

    @pytest.fixture
    def handler(self, task_repo, changelog_repo, permission_checker_stub, event_bus_stub) -> RemoveTaskFromSprintHandler:
        return RemoveTaskFromSprintHandler(
            task_repo=task_repo,
            changelog_repo=changelog_repo,
            permission_checker=permission_checker_stub,
            event_bus=event_bus_stub,
        )

    async def test_remove_from_sprint_success(self, handler, task_repo, make_task) -> None:
        sprint_id = Id.generate()
        task = await make_task()
        task.assign_to_sprint(sprint_id)
        task.clear_domain_events()
        await task_repo.update(task)

        cmd = RemoveTaskFromSprintCommand(
            caller_id=str(Id.generate()),
            task_id=str(task.id),
            changed_by=str(Id.generate()),
        )
        await handler.handle(cmd)

        found = await task_repo.get_by_id(task.id)
        assert found is not None
        assert found.sprint_id is None

    async def test_remove_from_sprint_creates_changelog(self, handler, changelog_repo, make_task) -> None:
        sprint_id = Id.generate()
        task = await make_task()
        task.assign_to_sprint(sprint_id)
        task.clear_domain_events()
        await handler._task_repo.update(task)

        cmd = RemoveTaskFromSprintCommand(
            caller_id=str(Id.generate()),
            task_id=str(task.id),
            changed_by=str(Id.generate()),
        )
        await handler.handle(cmd)

        entries = await changelog_repo.get_by_task_and_field(task.id, "sprint_id")
        assert len(entries) >= 1

    async def test_remove_from_sprint_not_found(self, handler) -> None:
        cmd = RemoveTaskFromSprintCommand(
            caller_id=str(Id.generate()),
            task_id=str(Id.generate()),
            changed_by=str(Id.generate()),
        )
        with pytest.raises(TaskNotFoundException):
            await handler.handle(cmd)

    async def test_remove_from_sprint_permission_denied(self, task_repo, changelog_repo, permission_denied_stub, event_bus_stub, make_task) -> None:
        task = await make_task()
        handler = RemoveTaskFromSprintHandler(task_repo=task_repo, changelog_repo=changelog_repo, permission_checker=permission_denied_stub, event_bus=event_bus_stub)
        cmd = RemoveTaskFromSprintCommand(
            caller_id=str(Id.generate()),
            task_id=str(task.id),
            changed_by=str(Id.generate()),
        )
        with pytest.raises(InsufficientTaskPermissionsException):
            await handler.handle(cmd)
