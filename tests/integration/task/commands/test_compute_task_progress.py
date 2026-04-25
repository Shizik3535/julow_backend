"""Интеграционные тесты ComputeTaskProgressHandler (реальные repos + стабы портов)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.task.application.commands.compute_task_progress import ComputeTaskProgressCommand, ComputeTaskProgressHandler
from app.context.task.application.exceptions.authorization_exceptions import InsufficientTaskPermissionsException
from app.context.task.domain.exceptions.task_exceptions import TaskNotFoundException


@pytest.mark.integration
class TestComputeTaskProgressHandler:
    """Тесты авто-расчёта прогресса из чек-листов — full stack."""

    @pytest.fixture
    def handler(self, task_repo, permission_checker_stub, event_bus_stub) -> ComputeTaskProgressHandler:
        return ComputeTaskProgressHandler(task_repo=task_repo, permission_checker=permission_checker_stub, event_bus=event_bus_stub)

    async def test_compute_progress_from_checklists(self, handler, task_repo, make_task) -> None:
        task = await make_task()
        cl = task.add_checklist("List")
        task.add_checklist_item(cl.id, "Item 1")
        task.add_checklist_item(cl.id, "Item 2")
        task.clear_domain_events()
        await task_repo.update(task)

        found = await task_repo.get_by_id(task.id)
        item1_id = found.checklists[0].items[0].id
        found.toggle_checklist_item(cl.id, item1_id)
        found.clear_domain_events()
        await task_repo.update(found)

        cmd = ComputeTaskProgressCommand(caller_id=str(Id.generate()), task_id=str(task.id))
        await handler.handle(cmd)

        updated = await task_repo.get_by_id(task.id)
        assert updated is not None
        assert updated.progress.value == 50

    async def test_compute_progress_no_checklists(self, handler, task_repo, make_task) -> None:
        task = await make_task()
        cmd = ComputeTaskProgressCommand(caller_id=str(Id.generate()), task_id=str(task.id))
        await handler.handle(cmd)

        found = await task_repo.get_by_id(task.id)
        assert found is not None
        assert found.progress.value == 0

    async def test_compute_progress_task_not_found(self, handler) -> None:
        cmd = ComputeTaskProgressCommand(caller_id=str(Id.generate()), task_id=str(Id.generate()))
        with pytest.raises(TaskNotFoundException):
            await handler.handle(cmd)

    async def test_compute_progress_permission_denied(self, task_repo, permission_denied_stub, event_bus_stub, make_task) -> None:
        task = await make_task()
        handler = ComputeTaskProgressHandler(task_repo=task_repo, permission_checker=permission_denied_stub, event_bus=event_bus_stub)
        cmd = ComputeTaskProgressCommand(caller_id=str(Id.generate()), task_id=str(task.id))
        with pytest.raises(InsufficientTaskPermissionsException):
            await handler.handle(cmd)
