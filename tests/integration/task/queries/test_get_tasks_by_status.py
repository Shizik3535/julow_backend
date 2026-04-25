"""Интеграционные тесты GetTasksByStatusHandler (реальные repos + стабы портов)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.task.application.queries.get_tasks_by_status import GetTasksByStatusQuery, GetTasksByStatusHandler
from app.context.task.application.exceptions.authorization_exceptions import InsufficientTaskPermissionsException


@pytest.mark.integration
class TestGetTasksByStatusHandler:
    """Тесты получения задач по статусу — full stack."""

    @pytest.fixture
    def handler(self, task_repo, permission_checker_stub) -> GetTasksByStatusHandler:
        return GetTasksByStatusHandler(task_repo=task_repo, permission_checker=permission_checker_stub)

    async def test_get_tasks_by_status_found(self, handler, task_repo, make_task) -> None:
        project_id = Id.generate()
        status_id = Id.generate()
        task = await make_task(project_id=project_id)
        task.change_status(status_id)
        task.clear_domain_events()
        await task_repo.update(task)

        result = await handler.handle(GetTasksByStatusQuery(caller_id=str(Id.generate()), project_id=str(project_id), status_id=str(status_id)))
        assert result.total >= 1

    async def test_get_tasks_by_status_empty(self, handler) -> None:
        result = await handler.handle(GetTasksByStatusQuery(caller_id=str(Id.generate()), project_id=str(Id.generate()), status_id=str(Id.generate())))
        assert result.total == 0

    async def test_get_tasks_by_status_permission_denied(self, task_repo, permission_denied_stub, make_task) -> None:
        project_id = Id.generate()
        status_id = Id.generate()
        task = await make_task(project_id=project_id)
        task.change_status(status_id)
        task.clear_domain_events()
        await task_repo.update(task)
        handler = GetTasksByStatusHandler(task_repo=task_repo, permission_checker=permission_denied_stub)
        with pytest.raises(InsufficientTaskPermissionsException):
            await handler.handle(GetTasksByStatusQuery(caller_id=str(Id.generate()), project_id=str(project_id), status_id=str(status_id)))
