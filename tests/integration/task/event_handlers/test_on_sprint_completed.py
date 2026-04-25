"""Интеграционные тесты OnSprintCompleted event handler (реальные repos + стабы портов)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.task.application.event_handlers.on_sprint_completed import OnSprintCompleted


@pytest.mark.integration
class TestOnSprintCompleted:
    """Тесты обработки события завершения спринта — full stack."""

    @pytest.fixture
    def handler(self, task_repo, event_bus_stub) -> OnSprintCompleted:
        return OnSprintCompleted(task_repo=task_repo, event_bus=event_bus_stub)

    async def test_removes_sprint_from_tasks(self, handler, task_repo, make_task) -> None:
        sprint_id = Id.generate()
        task = await make_task()
        task.assign_to_sprint(sprint_id)
        task.clear_domain_events()
        await task_repo.update(task)

        event = {"event_type": "SprintCompleted", "payload": {"sprint_id": str(sprint_id), "project_id": str(task.project_id)}}
        await handler.handle(event)

        found = await task_repo.get_by_id(task.id)
        assert found is not None
        assert found.sprint_id is None

    async def test_ignores_other_event_types(self, handler, task_repo, make_task) -> None:
        sprint_id = Id.generate()
        task = await make_task()
        task.assign_to_sprint(sprint_id)
        task.clear_domain_events()
        await task_repo.update(task)

        event = {"event_type": "SprintStarted", "payload": {"sprint_id": str(sprint_id), "project_id": str(task.project_id)}}
        await handler.handle(event)

        found = await task_repo.get_by_id(task.id)
        assert found is not None
        assert found.sprint_id == sprint_id
