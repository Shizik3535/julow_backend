"""Интеграционные тесты check_overdue_tasks — проверка публикации события TaskOverdue."""

from datetime import date, timedelta
from unittest.mock import AsyncMock

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.task.domain.aggregates.task import Task
from app.context.task.domain.value_objects.task_type import TaskType
from app.context.task.domain.events.task_events import TaskOverdue
from app.context.task.infrastructure.scheduling.check_overdue_tasks import check_overdue_tasks


class _StubCachePort:
    """In-memory stub для CachePort."""

    def __init__(self) -> None:
        self._store: dict[str, str] = {}

    async def get(self, key: str) -> str | None:
        return self._store.get(key)

    async def set(self, key: str, value: str, ttl: int | None = None) -> None:
        self._store[key] = value

    async def delete(self, key: str) -> None:
        self._store.pop(key, None)

    async def exists(self, key: str) -> bool:
        return key in self._store

    async def clear(self, pattern: str = "*") -> int:
        count = len(self._store)
        self._store.clear()
        return count


@pytest.mark.integration
class TestCheckOverdueTasks:
    """Тесты scheduled-задачи выявления просроченных задач."""

    @pytest.fixture
    def task_repo(self) -> AsyncMock:
        repo = AsyncMock()
        repo.get_overdue_tasks.return_value = []
        return repo

    @pytest.fixture
    def cache_port(self) -> _StubCachePort:
        return _StubCachePort()

    @pytest.fixture
    def event_bus(self) -> AsyncMock:
        return AsyncMock()

    async def test_no_overdue_tasks_no_events(
        self, task_repo, cache_port, event_bus
    ) -> None:
        task_repo.get_overdue_tasks.return_value = []

        await check_overdue_tasks(
            task_repo=task_repo,
            cache_port=cache_port,
            event_bus=event_bus,
        )

        event_bus.publish.assert_not_called()

    async def test_publishes_task_overdue_for_each_assignee(
        self, task_repo, cache_port, event_bus
    ) -> None:
        assignee1 = Id.generate()
        assignee2 = Id.generate()
        task = Task.create(
            title="Overdue Task",
            project_id=Id.generate(),
            task_type=TaskType.TASK,
            reporter_id=Id.generate(),
        )
        task.update_info(due_date=date.today() - timedelta(days=1))
        task.assign(assignee1)
        task.assign(assignee2)
        task.clear_domain_events()

        task_repo.get_overdue_tasks.return_value = [task]

        await check_overdue_tasks(
            task_repo=task_repo,
            cache_port=cache_port,
            event_bus=event_bus,
        )

        assert event_bus.publish.call_count == 2
        for call in event_bus.publish.call_args_list:
            event = call.args[0]
            assert isinstance(event, TaskOverdue)
            assert event.task_id == str(task.id)

    async def test_deduplication_skips_already_notified(
        self, task_repo, cache_port, event_bus
    ) -> None:
        assignee = Id.generate()
        task = Task.create(
            title="Overdue Task",
            project_id=Id.generate(),
            task_type=TaskType.TASK,
            reporter_id=Id.generate(),
        )
        task.update_info(due_date=date.today() - timedelta(days=1))
        task.assign(assignee)
        task.clear_domain_events()

        task_repo.get_overdue_tasks.return_value = [task]

        # First run — publishes event
        await check_overdue_tasks(
            task_repo=task_repo,
            cache_port=cache_port,
            event_bus=event_bus,
        )
        assert event_bus.publish.call_count == 1

        # Second run — skips (dedup key exists)
        event_bus.publish.reset_mock()
        await check_overdue_tasks(
            task_repo=task_repo,
            cache_port=cache_port,
            event_bus=event_bus,
        )
        event_bus.publish.assert_not_called()

    async def test_skips_task_without_due_date(
        self, task_repo, cache_port, event_bus
    ) -> None:
        assignee = Id.generate()
        task = Task.create(
            title="No Due Date",
            project_id=Id.generate(),
            task_type=TaskType.TASK,
            reporter_id=Id.generate(),
        )
        task.assign(assignee)
        task.clear_domain_events()

        # due_date is None, but repo returned it anyway
        task_repo.get_overdue_tasks.return_value = [task]

        await check_overdue_tasks(
            task_repo=task_repo,
            cache_port=cache_port,
            event_bus=event_bus,
        )

        event_bus.publish.assert_not_called()
