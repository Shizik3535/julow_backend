"""Интеграционные тесты CountTasksByProjectHandler (реальные repos + стабы портов)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.task.application.queries.count_tasks_by_project import CountTasksByProjectQuery, CountTasksByProjectHandler
from app.context.task.application.exceptions.authorization_exceptions import InsufficientTaskPermissionsException


@pytest.mark.integration
class TestCountTasksByProjectHandler:
    """Тесты подсчёта задач проекта — full stack."""

    @pytest.fixture
    def handler(self, task_repo, permission_checker_stub) -> CountTasksByProjectHandler:
        return CountTasksByProjectHandler(task_repo=task_repo, permission_checker=permission_checker_stub)

    async def test_count_tasks_by_project(self, handler, make_task) -> None:
        project_id = Id.generate()
        await make_task(project_id=project_id)
        await make_task(project_id=project_id)
        result = await handler.handle(CountTasksByProjectQuery(caller_id=str(Id.generate()), project_id=str(project_id)))
        assert result.count >= 2

    async def test_count_tasks_by_project_empty(self, handler) -> None:
        result = await handler.handle(CountTasksByProjectQuery(caller_id=str(Id.generate()), project_id=str(Id.generate())))
        assert result.count == 0

    async def test_count_tasks_permission_denied(self, task_repo, permission_denied_stub, make_task) -> None:
        project_id = Id.generate()
        await make_task(project_id=project_id)
        handler = CountTasksByProjectHandler(task_repo=task_repo, permission_checker=permission_denied_stub)
        with pytest.raises(InsufficientTaskPermissionsException):
            await handler.handle(CountTasksByProjectQuery(caller_id=str(Id.generate()), project_id=str(project_id)))
