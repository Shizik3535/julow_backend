"""Интеграционные тесты GetTasksByProjectHandler (реальные repos + стабы портов)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.task.application.queries.get_tasks_by_project import GetTasksByProjectQuery, GetTasksByProjectHandler
from app.context.task.application.exceptions.authorization_exceptions import InsufficientTaskPermissionsException


@pytest.mark.integration
class TestGetTasksByProjectHandler:
    """Тесты получения задач проекта — full stack."""

    @pytest.fixture
    def handler(self, task_repo, permission_checker_stub) -> GetTasksByProjectHandler:
        return GetTasksByProjectHandler(task_repo=task_repo, permission_checker=permission_checker_stub)

    async def test_get_tasks_by_project_found(self, handler, make_task) -> None:
        project_id = Id.generate()
        await make_task(project_id=project_id)
        result = await handler.handle(GetTasksByProjectQuery(caller_id=str(Id.generate()), project_id=str(project_id)))
        assert result.total >= 1

    async def test_get_tasks_by_project_empty(self, handler) -> None:
        result = await handler.handle(GetTasksByProjectQuery(caller_id=str(Id.generate()), project_id=str(Id.generate())))
        assert result.total == 0

    async def test_get_tasks_by_project_permission_denied(self, task_repo, permission_denied_stub, make_task) -> None:
        project_id = Id.generate()
        await make_task(project_id=project_id)
        handler = GetTasksByProjectHandler(task_repo=task_repo, permission_checker=permission_denied_stub)
        with pytest.raises(InsufficientTaskPermissionsException):
            await handler.handle(GetTasksByProjectQuery(caller_id=str(Id.generate()), project_id=str(project_id)))
