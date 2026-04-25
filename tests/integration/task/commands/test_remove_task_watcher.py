"""Интеграционные тесты RemoveTaskWatcherHandler (реальные repos + стабы портов)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.task.application.commands.remove_task_watcher import RemoveTaskWatcherCommand, RemoveTaskWatcherHandler
from app.context.task.application.exceptions.authorization_exceptions import InsufficientTaskPermissionsException
from app.context.task.domain.exceptions.task_exceptions import TaskNotFoundException


@pytest.mark.integration
class TestRemoveTaskWatcherHandler:
    """Тесты удаления наблюдателя — full stack."""

    @pytest.fixture
    def handler(self, task_repo, permission_checker_stub, event_bus_stub) -> RemoveTaskWatcherHandler:
        return RemoveTaskWatcherHandler(
            task_repo=task_repo,
            permission_checker=permission_checker_stub,
            event_bus=event_bus_stub,
        )

    async def test_remove_watcher_success(self, handler, task_repo, make_task) -> None:
        task = await make_task()
        watcher_id = Id.generate()
        task.add_watcher(watcher_id)
        task.clear_domain_events()
        await task_repo.update(task)

        cmd = RemoveTaskWatcherCommand(
            caller_id=str(watcher_id),
            task_id=str(task.id),
            user_id=str(watcher_id),
        )
        await handler.handle(cmd)

        found = await task_repo.get_by_id(task.id)
        assert found is not None
        assert len(found.watchers) == 0

    async def test_remove_watcher_task_not_found(self, handler) -> None:
        cmd = RemoveTaskWatcherCommand(
            caller_id=str(Id.generate()),
            task_id=str(Id.generate()),
            user_id=str(Id.generate()),
        )
        with pytest.raises(TaskNotFoundException):
            await handler.handle(cmd)

    async def test_remove_watcher_permission_denied(self, task_repo, permission_denied_stub, event_bus_stub, make_task) -> None:
        task = await make_task()
        watcher_id = Id.generate()
        task.add_watcher(watcher_id)
        task.clear_domain_events()
        await task_repo.update(task)
        handler = RemoveTaskWatcherHandler(
            task_repo=task_repo,
            permission_checker=permission_denied_stub,
            event_bus=event_bus_stub,
        )
        caller_id = Id.generate()
        cmd = RemoveTaskWatcherCommand(
            caller_id=str(caller_id),
            task_id=str(task.id),
            user_id=str(watcher_id),
        )
        with pytest.raises(InsufficientTaskPermissionsException):
            await handler.handle(cmd)
