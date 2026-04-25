"""Интеграционные тесты CountTasksByStatusHandler (реальные repos + стабы портов)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.task.application.queries.count_tasks_by_status import CountTasksByStatusQuery, CountTasksByStatusHandler
from app.context.task.application.exceptions.authorization_exceptions import InsufficientTaskPermissionsException


@pytest.mark.integration
class TestCountTasksByStatusHandler:
    """Тесты подсчёта задач по статусу — full stack."""

    @pytest.fixture
    def handler(self, task_repo, permission_checker_stub) -> CountTasksByStatusHandler:
        return CountTasksByStatusHandler(task_repo=task_repo, permission_checker=permission_checker_stub)

    async def test_count_tasks_by_status(self, handler, task_repo, make_task) -> None:
        project_id = Id.generate()
        status_id = Id.generate()
        task = await make_task(project_id=project_id)
        task.change_status(status_id)
        task.clear_domain_events()
        await task_repo.update(task)

        result = await handler.handle(CountTasksByStatusQuery(caller_id=str(Id.generate()), project_id=str(project_id), status_id=str(status_id)))
        assert result.count >= 1

    async def test_count_tasks_by_status_empty(self, handler) -> None:
        result = await handler.handle(CountTasksByStatusQuery(caller_id=str(Id.generate()), project_id=str(Id.generate()), status_id=str(Id.generate())))
        assert result.count == 0

    async def test_count_by_status_permission_denied(self, task_repo, permission_denied_stub, make_task) -> None:
        project_id = Id.generate()
        task = await make_task(project_id=project_id)
        handler = CountTasksByStatusHandler(task_repo=task_repo, permission_checker=permission_denied_stub)
        with pytest.raises(InsufficientTaskPermissionsException):
            await handler.handle(CountTasksByStatusQuery(caller_id=str(Id.generate()), project_id=str(project_id), status_id=str(Id.generate())))
