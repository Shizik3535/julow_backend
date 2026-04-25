"""Интеграционные тесты GetTasksByEpicHandler (реальные repos + стабы портов)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.task.application.queries.get_tasks_by_epic import GetTasksByEpicQuery, GetTasksByEpicHandler
from app.context.task.application.exceptions.authorization_exceptions import InsufficientTaskPermissionsException


@pytest.mark.integration
class TestGetTasksByEpicHandler:
    """Тесты получения задач эпика — full stack."""

    @pytest.fixture
    def handler(self, task_repo, permission_checker_stub) -> GetTasksByEpicHandler:
        return GetTasksByEpicHandler(task_repo=task_repo, permission_checker=permission_checker_stub)

    async def test_get_tasks_by_epic_found(self, handler, make_task) -> None:
        epic_id = Id.generate()
        await make_task(epic_id=epic_id)
        result = await handler.handle(GetTasksByEpicQuery(caller_id=str(Id.generate()), epic_id=str(epic_id), project_id=str(Id.generate())))
        assert result.total >= 1

    async def test_get_tasks_by_epic_empty(self, handler) -> None:
        result = await handler.handle(GetTasksByEpicQuery(caller_id=str(Id.generate()), epic_id=str(Id.generate()), project_id=str(Id.generate())))
        assert result.total == 0

    async def test_get_tasks_by_epic_permission_denied(self, task_repo, permission_denied_stub, make_task) -> None:
        epic_id = Id.generate()
        await make_task(epic_id=epic_id)
        handler = GetTasksByEpicHandler(task_repo=task_repo, permission_checker=permission_denied_stub)
        with pytest.raises(InsufficientTaskPermissionsException):
            await handler.handle(GetTasksByEpicQuery(caller_id=str(Id.generate()), epic_id=str(epic_id), project_id=str(Id.generate())))
