"""Интеграционные тесты OnTaskCompletedCreateRecurring event handler (реальные repos + стабы портов)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.task.application.event_handlers.on_task_completed_create_recurring import OnTaskCompletedCreateRecurring
from app.context.task.domain.events.task_events import TaskStatusChanged
from app.context.task.domain.value_objects.recurrence_config import RecurrenceConfig
from app.context.task.domain.value_objects.recurrence_pattern import RecurrencePattern


@pytest.mark.integration
class TestOnTaskCompletedCreateRecurring:
    """Тесты обработки события завершения повторяющейся задачи — full stack."""

    @pytest.fixture
    def handler(self, task_repo, event_bus_stub) -> OnTaskCompletedCreateRecurring:
        done_status_id = str(Id.generate())
        return OnTaskCompletedCreateRecurring(task_repo=task_repo, event_bus=event_bus_stub, done_status_ids=[done_status_id])

    async def test_creates_recurring_task(self, handler, task_repo, make_task) -> None:
        task = await make_task()
        task.set_recurrence(RecurrenceConfig(pattern=RecurrencePattern.WEEKLY, interval=1))
        task.clear_domain_events()
        await task_repo.update(task)

        event = TaskStatusChanged(task_id=str(task.id), new_status_id=handler._done_status_ids[0])
        await handler.handle(event)

        tasks = await task_repo.get_by_project(task.project_id)
        assert len(tasks) >= 2

    async def test_skips_non_done_status(self, handler, task_repo, make_task) -> None:
        task = await make_task()
        task.set_recurrence(RecurrenceConfig(pattern=RecurrencePattern.WEEKLY, interval=1))
        task.clear_domain_events()
        await task_repo.update(task)

        event = TaskStatusChanged(task_id=str(task.id), new_status_id=str(Id.generate()))
        await handler.handle(event)

        tasks = await task_repo.get_by_project(task.project_id)
        assert len(tasks) == 1

    async def test_skips_task_without_recurrence(self, handler, task_repo, make_task) -> None:
        task = await make_task()

        event = TaskStatusChanged(task_id=str(task.id), new_status_id=handler._done_status_ids[0])
        await handler.handle(event)

        tasks = await task_repo.get_by_project(task.project_id)
        assert len(tasks) == 1
