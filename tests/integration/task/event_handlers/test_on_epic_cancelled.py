"""Интеграционные тесты OnEpicCancelled event handler (реальные repos + стабы портов)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.task.application.event_handlers.on_epic_cancelled import OnEpicCancelled


@pytest.mark.integration
class TestOnEpicCancelled:
    """Тесты обработки события отмены эпика — full stack."""

    @pytest.fixture
    def handler(self, task_repo, event_bus_stub) -> OnEpicCancelled:
        return OnEpicCancelled(task_repo=task_repo, event_bus=event_bus_stub)

    async def test_removes_epic_from_tasks(self, handler, task_repo, make_task) -> None:
        epic_id = Id.generate()
        task = await make_task(epic_id=epic_id)

        event = {"event_type": "EpicStatusChanged", "payload": {"epic_id": str(epic_id), "new_status": "CANCELLED"}}
        await handler.handle(event)

        found = await task_repo.get_by_id(task.id)
        assert found is not None
        assert found.epic_id is None

    async def test_ignores_non_cancelled_status(self, handler, task_repo, make_task) -> None:
        epic_id = Id.generate()
        task = await make_task(epic_id=epic_id)

        event = {"event_type": "EpicStatusChanged", "payload": {"epic_id": str(epic_id), "new_status": "ACTIVE"}}
        await handler.handle(event)

        found = await task_repo.get_by_id(task.id)
        assert found is not None
        assert found.epic_id == epic_id

    async def test_ignores_other_event_types(self, handler, task_repo, make_task) -> None:
        epic_id = Id.generate()
        task = await make_task(epic_id=epic_id)

        event = {"event_type": "EpicCreated", "payload": {"epic_id": str(epic_id), "new_status": "CANCELLED"}}
        await handler.handle(event)

        found = await task_repo.get_by_id(task.id)
        assert found is not None
        assert found.epic_id == epic_id
