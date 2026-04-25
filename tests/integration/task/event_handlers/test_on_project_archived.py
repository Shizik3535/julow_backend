"""Интеграционные тесты OnProjectArchived event handler (реальные repos + стабы портов)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.task.application.event_handlers.on_project_archived import OnProjectArchived
from app.context.task.domain.value_objects.task_status import TaskStatus


@pytest.mark.integration
class TestOnProjectArchived:
    """Тесты обработки события архивирования проекта — full stack."""

    @pytest.fixture
    def handler(self, task_repo, event_bus_stub) -> OnProjectArchived:
        return OnProjectArchived(task_repo=task_repo, event_bus=event_bus_stub)

    async def test_archives_all_project_tasks(self, handler, task_repo, make_task) -> None:
        project_id = Id.generate()
        task1 = await make_task(project_id=project_id)
        task2 = await make_task(project_id=project_id)

        event = {"event_type": "ProjectArchived", "payload": {"project_id": str(project_id)}}
        await handler.handle(event)

        found1 = await task_repo.get_by_id(task1.id)
        found2 = await task_repo.get_by_id(task2.id)
        assert found1 is not None
        assert found2 is not None
        assert found1.status == TaskStatus.ARCHIVED
        assert found2.status == TaskStatus.ARCHIVED

    async def test_no_tasks_ignores(self, handler) -> None:
        event = {"event_type": "ProjectArchived", "payload": {"project_id": str(Id.generate())}}
        await handler.handle(event)

    async def test_ignores_other_event_types(self, handler, task_repo, make_task) -> None:
        task = await make_task()
        event = {"event_type": "ProjectCreated", "payload": {"project_id": str(task.project_id)}}
        await handler.handle(event)

        found = await task_repo.get_by_id(task.id)
        assert found is not None
        assert found.status == TaskStatus.ACTIVE
