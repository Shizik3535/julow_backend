"""Интеграционные тесты TaskProviderAdapter (outboard adapter внутри Task BC)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.task.infrastructure.integration.outboard.task_provider_adapter import TaskProviderAdapter


@pytest.mark.integration
class TestTaskProviderAdapter:
    """Тесты outboard-адаптера TaskProvider — full stack."""

    @pytest.fixture
    def adapter(self, task_repo) -> TaskProviderAdapter:
        return TaskProviderAdapter(repo=task_repo)

    async def test_task_exists(self, adapter, make_task) -> None:
        task = await make_task()
        assert await adapter.task_exists(str(task.id)) is True

    async def test_task_not_exists(self, adapter) -> None:
        assert await adapter.task_exists(str(Id.generate())) is False

    async def test_get_task(self, adapter, make_task) -> None:
        task = await make_task(title="Adapter Task")
        result = await adapter.get_task(str(task.id))
        assert result is not None
        assert result.title == "Adapter Task"

    async def test_get_task_not_found(self, adapter) -> None:
        result = await adapter.get_task(str(Id.generate()))
        assert result is None

    async def test_get_tasks_by_project(self, adapter, make_task) -> None:
        project_id = Id.generate()
        await make_task(project_id=project_id)
        results = await adapter.get_tasks_by_project(str(project_id))
        assert len(results) >= 1

    async def test_count_by_project(self, adapter, make_task) -> None:
        project_id = Id.generate()
        await make_task(project_id=project_id)
        count = await adapter.count_by_project(str(project_id))
        assert count >= 1
