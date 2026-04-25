"""Интеграционные тесты ArchiveTaskHandler (реальные repos + стабы портов)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.task.application.commands.archive_task import ArchiveTaskCommand, ArchiveTaskHandler
from app.context.task.domain.exceptions.task_exceptions import TaskNotFoundException
from app.context.task.domain.value_objects.task_status import TaskStatus


@pytest.mark.integration
class TestArchiveTaskHandler:
    """Тесты архивирования задачи — full stack."""

    @pytest.fixture
    def handler(self, task_repo, permission_checker_stub, event_bus_stub) -> ArchiveTaskHandler:
        return ArchiveTaskHandler(
            task_repo=task_repo,
            permission_checker=permission_checker_stub,
            event_bus=event_bus_stub,
        )

    async def test_archive_task_success(self, handler, task_repo, make_task) -> None:
        task = await make_task()
        cmd = ArchiveTaskCommand(
            caller_id=str(Id.generate()),
            task_id=str(task.id),
        )
        await handler.handle(cmd)

        found = await task_repo.get_by_id(task.id)
        assert found is not None
        assert found.status == TaskStatus.ARCHIVED

    async def test_archive_task_not_found(self, handler) -> None:
        cmd = ArchiveTaskCommand(
            caller_id=str(Id.generate()),
            task_id=str(Id.generate()),
        )
        with pytest.raises(TaskNotFoundException):
            await handler.handle(cmd)
