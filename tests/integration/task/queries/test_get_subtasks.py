"""Интеграционные тесты GetSubtasksHandler (реальные repos + стабы портов)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.task.application.queries.get_subtasks import GetSubtasksQuery, GetSubtasksHandler
from app.context.task.application.exceptions.authorization_exceptions import InsufficientTaskPermissionsException


@pytest.mark.integration
class TestGetSubtasksHandler:
    """Тесты получения подзадач — full stack."""

    @pytest.fixture
    def handler(self, task_repo, permission_checker_stub) -> GetSubtasksHandler:
        return GetSubtasksHandler(task_repo=task_repo, permission_checker=permission_checker_stub)

    async def test_get_subtasks_found(self, handler, make_task) -> None:
        parent = await make_task()
        await make_task(title="Child", parent_task_id=parent.id)
        result = await handler.handle(GetSubtasksQuery(caller_id=str(Id.generate()), parent_task_id=str(parent.id)))
        assert result.total >= 1

    async def test_get_subtasks_empty(self, handler, make_task) -> None:
        parent = await make_task()
        result = await handler.handle(GetSubtasksQuery(caller_id=str(Id.generate()), parent_task_id=str(parent.id)))
        assert result.total == 0

    async def test_get_subtasks_permission_denied(self, task_repo, permission_denied_stub, make_task) -> None:
        parent = await make_task()
        handler = GetSubtasksHandler(task_repo=task_repo, permission_checker=permission_denied_stub)
        with pytest.raises(InsufficientTaskPermissionsException):
            await handler.handle(GetSubtasksQuery(caller_id=str(Id.generate()), parent_task_id=str(parent.id)))
