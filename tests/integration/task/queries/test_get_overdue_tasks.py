"""Интеграционные тесты GetOverdueTasksHandler (реальные repos + стабы портов)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.task.application.queries.get_overdue_tasks import GetOverdueTasksQuery, GetOverdueTasksHandler
from app.context.task.application.exceptions.authorization_exceptions import InsufficientTaskPermissionsException


@pytest.mark.integration
class TestGetOverdueTasksHandler:
    """Тесты получения просроченных задач — full stack."""

    @pytest.fixture
    def handler(self, task_repo, permission_checker_stub) -> GetOverdueTasksHandler:
        return GetOverdueTasksHandler(task_repo=task_repo, permission_checker=permission_checker_stub)

    async def test_get_overdue_tasks_returns_list(self, handler) -> None:
        result = await handler.handle(GetOverdueTasksQuery(caller_id=str(Id.generate())))
        assert result.items is not None

    async def test_get_overdue_tasks_with_project_permission_denied(self, task_repo, permission_denied_stub) -> None:
        handler = GetOverdueTasksHandler(task_repo=task_repo, permission_checker=permission_denied_stub)
        with pytest.raises(InsufficientTaskPermissionsException):
            await handler.handle(GetOverdueTasksQuery(caller_id=str(Id.generate()), project_id=str(Id.generate())))
