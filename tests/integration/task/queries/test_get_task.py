"""Интеграционные тесты GetTaskHandler (реальные repos + стабы портов)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.task.application.queries.get_task import GetTaskQuery, GetTaskHandler
from app.context.task.application.exceptions.authorization_exceptions import InsufficientTaskPermissionsException
from app.context.task.domain.exceptions.task_exceptions import TaskNotFoundException


@pytest.mark.integration
class TestGetTaskHandler:
    """Тесты получения задачи по ID — full stack."""

    @pytest.fixture
    def handler(self, task_repo, permission_checker_stub) -> GetTaskHandler:
        return GetTaskHandler(task_repo=task_repo, permission_checker=permission_checker_stub)

    async def test_get_task_found(self, handler, make_task) -> None:
        task = await make_task(title="FindMe")
        result = await handler.handle(GetTaskQuery(task_id=str(task.id), caller_id=str(Id.generate())))
        assert result.title == "FindMe"
        assert result.id == str(task.id)

    async def test_get_task_not_found(self, handler) -> None:
        with pytest.raises(TaskNotFoundException):
            await handler.handle(GetTaskQuery(task_id=str(Id.generate()), caller_id=str(Id.generate())))

    async def test_get_task_with_labels(self, handler, task_repo, make_task) -> None:
        from app.context.task.domain.value_objects.label import Label

        task = await make_task()
        task.add_label(Label(name="bug", color=None))
        task.clear_domain_events()
        await task_repo.update(task)

        result = await handler.handle(GetTaskQuery(task_id=str(task.id), caller_id=str(Id.generate())))
        assert len(result.labels) >= 1

    async def test_get_task_permission_denied(self, task_repo, permission_denied_stub, make_task) -> None:
        task = await make_task()
        handler = GetTaskHandler(task_repo=task_repo, permission_checker=permission_denied_stub)
        with pytest.raises(InsufficientTaskPermissionsException):
            await handler.handle(GetTaskQuery(task_id=str(task.id), caller_id=str(Id.generate())))
