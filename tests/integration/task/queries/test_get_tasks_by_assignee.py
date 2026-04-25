"""Интеграционные тесты GetTasksByAssigneeHandler (реальные repos + стабы портов)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.task.application.queries.get_tasks_by_assignee import GetTasksByAssigneeQuery, GetTasksByAssigneeHandler
from app.context.task.application.exceptions.authorization_exceptions import InsufficientTaskPermissionsException


@pytest.mark.integration
class TestGetTasksByAssigneeHandler:
    """Тесты получения задач исполнителя — full stack."""

    @pytest.fixture
    def handler(self, task_repo, permission_checker_stub) -> GetTasksByAssigneeHandler:
        return GetTasksByAssigneeHandler(task_repo=task_repo, permission_checker=permission_checker_stub)

    async def test_get_tasks_by_assignee_found(self, handler, task_repo, make_task) -> None:
        task = await make_task()
        assignee_id = Id.generate()
        task.assign(assignee_id)
        task.clear_domain_events()
        await task_repo.update(task)

        result = await handler.handle(GetTasksByAssigneeQuery(caller_id=str(assignee_id), assignee_id=str(assignee_id)))
        assert result.total >= 1

    async def test_get_tasks_by_assignee_empty(self, handler) -> None:
        result = await handler.handle(GetTasksByAssigneeQuery(caller_id=str(Id.generate()), assignee_id=str(Id.generate())))
        assert result.total == 0

    async def test_get_tasks_by_assignee_with_project_permission_denied(self, task_repo, permission_denied_stub, make_task) -> None:
        task = await make_task()
        assignee_id = Id.generate()
        task.assign(assignee_id)
        task.clear_domain_events()
        await task_repo.update(task)
        handler = GetTasksByAssigneeHandler(task_repo=task_repo, permission_checker=permission_denied_stub)
        with pytest.raises(InsufficientTaskPermissionsException):
            await handler.handle(GetTasksByAssigneeQuery(caller_id=str(Id.generate()), assignee_id=str(assignee_id), project_id=str(Id.generate())))
