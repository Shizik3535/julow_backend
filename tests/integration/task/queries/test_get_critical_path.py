"""Интеграционные тесты для GetCriticalPathHandler (CPM — критический путь)."""

from __future__ import annotations

from datetime import date
from unittest.mock import AsyncMock

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.task.domain.aggregates.task import Task
from app.context.task.domain.value_objects.task_type import TaskType
from app.context.task.domain.value_objects.relation_type import RelationType
from app.context.task.application.queries.get_critical_path import (
    GetCriticalPathHandler,
    GetCriticalPathQuery,
    CriticalPathDTO,
)


def _make_task(
    project_id: Id,
    start: date | None = None,
    due: date | None = None,
    title: str = "Task",
) -> Task:
    """Создать задачу с указанными датами."""
    task = Task.create(
        title=title,
        project_id=project_id,
        task_type=TaskType.TASK,
        reporter_id=Id.generate(),
    )
    task.start_date = start
    task.due_date = due
    task.clear_domain_events()
    return task


def _add_blocks_relation(blocker: Task, blocked: Task) -> None:
    """Добавить связь BLOCKS от blocker к blocked."""
    blocker.add_relation(
        related_task_id=blocked.id,
        relation_type=RelationType.BLOCKS,
        created_by=Id.generate(),
    )
    blocker.clear_domain_events()


@pytest.fixture
def project_id() -> Id:
    return Id.generate()


@pytest.fixture
def permission_checker() -> AsyncMock:
    checker = AsyncMock()
    checker.require_permission = AsyncMock(return_value=None)
    return checker


@pytest.mark.integration
class TestGetCriticalPathHandler:
    """Тесты CPM-алгоритма."""

    @pytest.mark.asyncio
    async def test_empty_project(self, project_id: Id, permission_checker: AsyncMock) -> None:
        """Пустой проект — пустой результат."""
        task_repo = AsyncMock()
        task_repo.get_by_project = AsyncMock(return_value=[])

        handler = GetCriticalPathHandler(
            task_repo=task_repo,
            permission_checker=permission_checker,
        )
        query = GetCriticalPathQuery(caller_id="user-1", project_id=str(project_id))
        result = await handler.handle(query)

        assert isinstance(result, CriticalPathDTO)
        assert result.path == []
        assert result.total_duration_days == 0

    @pytest.mark.asyncio
    async def test_linear_chain(self, project_id: Id, permission_checker: AsyncMock) -> None:
        """Линейная цепочка A→B→C — все на критическом пути."""
        task_a = _make_task(project_id, date(2025, 1, 1), date(2025, 1, 4), "A")  # 3 days
        task_b = _make_task(project_id, date(2025, 1, 4), date(2025, 1, 6), "B")  # 2 days
        task_c = _make_task(project_id, date(2025, 1, 6), date(2025, 1, 9), "C")  # 3 days

        _add_blocks_relation(task_a, task_b)
        _add_blocks_relation(task_b, task_c)

        task_repo = AsyncMock()
        task_repo.get_by_project = AsyncMock(return_value=[task_a, task_b, task_c])

        handler = GetCriticalPathHandler(
            task_repo=task_repo,
            permission_checker=permission_checker,
        )
        query = GetCriticalPathQuery(caller_id="user-1", project_id=str(project_id))
        result = await handler.handle(query)

        assert len(result.path) == 3
        path_ids = {n.task_id for n in result.path}
        assert str(task_a.id) in path_ids
        assert str(task_b.id) in path_ids
        assert str(task_c.id) in path_ids
        assert result.total_duration_days == 8

    @pytest.mark.asyncio
    async def test_parallel_branches_short_branch_excluded(
        self, project_id: Id, permission_checker: AsyncMock
    ) -> None:
        """Параллельные ветви — короткая ветвь не на критическом пути."""
        task_start = _make_task(project_id, date(2025, 1, 1), date(2025, 1, 3), "Start")  # 2 days
        task_long = _make_task(project_id, date(2025, 1, 3), date(2025, 1, 8), "Long")  # 5 days
        task_short = _make_task(project_id, date(2025, 1, 3), date(2025, 1, 4), "Short")  # 1 day
        task_end = _make_task(project_id, date(2025, 1, 8), date(2025, 1, 10), "End")  # 2 days

        _add_blocks_relation(task_start, task_long)
        _add_blocks_relation(task_start, task_short)
        _add_blocks_relation(task_long, task_end)
        _add_blocks_relation(task_short, task_end)

        task_repo = AsyncMock()
        task_repo.get_by_project = AsyncMock(
            return_value=[task_start, task_long, task_short, task_end]
        )

        handler = GetCriticalPathHandler(
            task_repo=task_repo,
            permission_checker=permission_checker,
        )
        query = GetCriticalPathQuery(caller_id="user-1", project_id=str(project_id))
        result = await handler.handle(query)

        critical_ids = {n.task_id for n in result.path}
        assert str(task_start.id) in critical_ids
        assert str(task_long.id) in critical_ids
        assert str(task_end.id) in critical_ids
        assert str(task_short.id) not in critical_ids
        assert result.total_duration_days == 9

    @pytest.mark.asyncio
    async def test_tasks_without_dates_get_zero_duration(
        self, project_id: Id, permission_checker: AsyncMock
    ) -> None:
        """Задачи без дат получают duration=0."""
        task_a = _make_task(project_id, date(2025, 1, 1), date(2025, 1, 5), "A")  # 4 days
        task_b = _make_task(project_id, None, None, "B")  # no dates → duration=0

        task_repo = AsyncMock()
        task_repo.get_by_project = AsyncMock(return_value=[task_a, task_b])

        handler = GetCriticalPathHandler(
            task_repo=task_repo,
            permission_checker=permission_checker,
        )
        query = GetCriticalPathQuery(caller_id="user-1", project_id=str(project_id))
        result = await handler.handle(query)

        critical_ids = {n.task_id for n in result.path}
        assert str(task_a.id) in critical_ids
        assert result.total_duration_days == 4

    @pytest.mark.asyncio
    async def test_cyclic_dependency_returns_empty(
        self, project_id: Id, permission_checker: AsyncMock
    ) -> None:
        """Циклическая зависимость — топологическая сортировка провалится, пустой результат."""
        task_a = _make_task(project_id, date(2025, 1, 1), date(2025, 1, 3), "A")
        task_b = _make_task(project_id, date(2025, 1, 3), date(2025, 1, 5), "B")

        _add_blocks_relation(task_a, task_b)
        _add_blocks_relation(task_b, task_a)

        task_repo = AsyncMock()
        task_repo.get_by_project = AsyncMock(return_value=[task_a, task_b])

        handler = GetCriticalPathHandler(
            task_repo=task_repo,
            permission_checker=permission_checker,
        )
        query = GetCriticalPathQuery(caller_id="user-1", project_id=str(project_id))
        result = await handler.handle(query)

        assert result.path == []
        assert result.total_duration_days == 0
