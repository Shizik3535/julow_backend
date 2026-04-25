"""Интеграционные тесты RemoveTaskFromEpicHandler (реальные repos + стабы портов)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.task.application.commands.remove_task_from_epic import RemoveTaskFromEpicCommand, RemoveTaskFromEpicHandler
from app.context.task.application.exceptions.authorization_exceptions import InsufficientTaskPermissionsException
from app.context.task.domain.exceptions.task_exceptions import TaskNotFoundException


@pytest.mark.integration
class TestRemoveTaskFromEpicHandler:
    """Тесты отвязки задачи от эпика — full stack."""

    @pytest.fixture
    def handler(self, task_repo, changelog_repo, permission_checker_stub, event_bus_stub) -> RemoveTaskFromEpicHandler:
        return RemoveTaskFromEpicHandler(
            task_repo=task_repo,
            changelog_repo=changelog_repo,
            permission_checker=permission_checker_stub,
            event_bus=event_bus_stub,
        )

    async def test_remove_from_epic_success(self, handler, task_repo, make_task) -> None:
        epic_id = Id.generate()
        task = await make_task(epic_id=epic_id)

        cmd = RemoveTaskFromEpicCommand(
            caller_id=str(Id.generate()),
            task_id=str(task.id),
            changed_by=str(Id.generate()),
        )
        await handler.handle(cmd)

        found = await task_repo.get_by_id(task.id)
        assert found is not None
        assert found.epic_id is None

    async def test_remove_from_epic_creates_changelog(self, handler, changelog_repo, make_task) -> None:
        epic_id = Id.generate()
        task = await make_task(epic_id=epic_id)

        cmd = RemoveTaskFromEpicCommand(
            caller_id=str(Id.generate()),
            task_id=str(task.id),
            changed_by=str(Id.generate()),
        )
        await handler.handle(cmd)

        entries = await changelog_repo.get_by_task_and_field(task.id, "epic_id")
        assert len(entries) >= 1

    async def test_remove_from_epic_not_found(self, handler) -> None:
        cmd = RemoveTaskFromEpicCommand(
            caller_id=str(Id.generate()),
            task_id=str(Id.generate()),
            changed_by=str(Id.generate()),
        )
        with pytest.raises(TaskNotFoundException):
            await handler.handle(cmd)

    async def test_remove_from_epic_permission_denied(self, task_repo, changelog_repo, permission_denied_stub, event_bus_stub, make_task) -> None:
        task = await make_task()
        handler = RemoveTaskFromEpicHandler(task_repo=task_repo, changelog_repo=changelog_repo, permission_checker=permission_denied_stub, event_bus=event_bus_stub)
        cmd = RemoveTaskFromEpicCommand(
            caller_id=str(Id.generate()),
            task_id=str(task.id),
            changed_by=str(Id.generate()),
        )
        with pytest.raises(InsufficientTaskPermissionsException):
            await handler.handle(cmd)
