"""Интеграционные тесты GetTasksBySprintHandler (реальные repos + стабы портов)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.task.application.queries.get_tasks_by_sprint import GetTasksBySprintQuery, GetTasksBySprintHandler
from app.context.task.application.exceptions.authorization_exceptions import InsufficientTaskPermissionsException


@pytest.mark.integration
class TestGetTasksBySprintHandler:
    """Тесты получения задач спринта — full stack."""

    @pytest.fixture
    def handler(self, task_repo, permission_checker_stub) -> GetTasksBySprintHandler:
        return GetTasksBySprintHandler(task_repo=task_repo, permission_checker=permission_checker_stub)

    async def test_get_tasks_by_sprint_found(self, handler, task_repo, make_task) -> None:
        sprint_id = Id.generate()
        task = await make_task()
        task.assign_to_sprint(sprint_id)
        task.clear_domain_events()
        await task_repo.update(task)

        result = await handler.handle(GetTasksBySprintQuery(caller_id=str(Id.generate()), sprint_id=str(sprint_id), project_id=str(Id.generate())))
        assert result.total >= 1

    async def test_get_tasks_by_sprint_empty(self, handler) -> None:
        result = await handler.handle(GetTasksBySprintQuery(caller_id=str(Id.generate()), sprint_id=str(Id.generate()), project_id=str(Id.generate())))
        assert result.total == 0

    async def test_get_tasks_by_sprint_permission_denied(self, task_repo, permission_denied_stub, make_task) -> None:
        sprint_id = Id.generate()
        task = await make_task()
        task.assign_to_sprint(sprint_id)
        task.clear_domain_events()
        await task_repo.update(task)
        handler = GetTasksBySprintHandler(task_repo=task_repo, permission_checker=permission_denied_stub)
        with pytest.raises(InsufficientTaskPermissionsException):
            await handler.handle(GetTasksBySprintQuery(caller_id=str(Id.generate()), sprint_id=str(sprint_id), project_id=str(Id.generate())))
