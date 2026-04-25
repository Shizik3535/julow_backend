"""Интеграционные тесты GetTasksByReporterHandler (реальные repos + стабы портов)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.task.application.queries.get_tasks_by_reporter import GetTasksByReporterQuery, GetTasksByReporterHandler
from app.context.task.application.exceptions.authorization_exceptions import InsufficientTaskPermissionsException


@pytest.mark.integration
class TestGetTasksByReporterHandler:
    """Тесты получения задач автора — full stack."""

    @pytest.fixture
    def handler(self, task_repo, permission_checker_stub) -> GetTasksByReporterHandler:
        return GetTasksByReporterHandler(task_repo=task_repo, permission_checker=permission_checker_stub)

    async def test_get_tasks_by_reporter_found(self, handler, make_task) -> None:
        reporter_id = Id.generate()
        await make_task(reporter_id=reporter_id)
        result = await handler.handle(GetTasksByReporterQuery(caller_id=str(reporter_id), reporter_id=str(reporter_id)))
        assert result.total >= 1

    async def test_get_tasks_by_reporter_empty(self, handler) -> None:
        result = await handler.handle(GetTasksByReporterQuery(caller_id=str(Id.generate()), reporter_id=str(Id.generate())))
        assert result.total == 0

    async def test_get_tasks_by_reporter_with_project_permission_denied(self, task_repo, permission_denied_stub, make_task) -> None:
        reporter_id = Id.generate()
        await make_task(reporter_id=reporter_id)
        handler = GetTasksByReporterHandler(task_repo=task_repo, permission_checker=permission_denied_stub)
        with pytest.raises(InsufficientTaskPermissionsException):
            await handler.handle(GetTasksByReporterQuery(caller_id=str(Id.generate()), reporter_id=str(reporter_id), project_id=str(Id.generate())))
