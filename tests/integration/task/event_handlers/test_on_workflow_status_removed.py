"""Интеграционные тесты OnWorkflowStatusRemoved event handler (реальные repos + стабы портов)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.task.application.event_handlers.on_workflow_status_removed import OnWorkflowStatusRemoved


@pytest.mark.integration
class TestOnWorkflowStatusRemoved:
    """Тесты обработки события удаления workflow-статуса — full stack."""

    @pytest.fixture
    def handler(self, task_repo, board_stub, event_bus_stub) -> OnWorkflowStatusRemoved:
        return OnWorkflowStatusRemoved(task_repo=task_repo, board_port=board_stub, event_bus=event_bus_stub)

    async def test_resets_status_id_on_tasks(self, handler, task_repo, board_stub, make_task) -> None:
        project_id = Id.generate()
        removed_status_id = Id.generate()
        task = await make_task(project_id=project_id)
        task.change_status(removed_status_id)
        task.clear_domain_events()
        await task_repo.update(task)

        event = {
            "event_type": "WorkflowStatusRemoved",
            "payload": {
                "project_id": str(project_id),
                "status_id": str(removed_status_id),
            },
        }
        await handler.handle(event)

        found = await task_repo.get_by_id(task.id)
        assert found is not None
        assert found.status_id == Id.from_string(board_stub._default_status_id)

    async def test_ignores_other_event_types(self, handler, task_repo, make_task) -> None:
        project_id = Id.generate()
        status_id = Id.generate()
        task = await make_task(project_id=project_id)
        task.change_status(status_id)
        task.clear_domain_events()
        await task_repo.update(task)

        event = {
            "event_type": "WorkflowStatusAdded",
            "payload": {
                "project_id": str(project_id),
                "status_id": str(status_id),
            },
        }
        await handler.handle(event)

        found = await task_repo.get_by_id(task.id)
        assert found is not None
        assert found.status_id == status_id
