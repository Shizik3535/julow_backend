"""Интеграционные тесты GetTasksByLabelsHandler (реальные repos + стабы портов)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.task.application.queries.get_tasks_by_labels import GetTasksByLabelsQuery, GetTasksByLabelsHandler
from app.context.task.application.exceptions.authorization_exceptions import InsufficientTaskPermissionsException


@pytest.mark.integration
class TestGetTasksByLabelsHandler:
    """Тесты получения задач по меткам — full stack."""

    @pytest.fixture
    def handler(self, task_repo, permission_checker_stub) -> GetTasksByLabelsHandler:
        return GetTasksByLabelsHandler(task_repo=task_repo, permission_checker=permission_checker_stub)

    async def test_get_tasks_by_labels_found(self, handler, task_repo, make_task) -> None:
        from app.context.task.domain.value_objects.label import Label

        project_id = Id.generate()
        task = await make_task(project_id=project_id)
        task.add_label(Label(name="backend", color=None))
        task.clear_domain_events()
        await task_repo.update(task)

        result = await handler.handle(GetTasksByLabelsQuery(caller_id=str(Id.generate()), project_id=str(project_id), label_names=["backend"]))
        assert result.total >= 1

    async def test_get_tasks_by_labels_empty(self, handler) -> None:
        result = await handler.handle(GetTasksByLabelsQuery(caller_id=str(Id.generate()), project_id=str(Id.generate()), label_names=["nonexistent"]))
        assert result.total == 0

    async def test_get_tasks_by_labels_permission_denied(self, task_repo, permission_denied_stub, make_task) -> None:
        project_id = Id.generate()
        await make_task(project_id=project_id)
        handler = GetTasksByLabelsHandler(task_repo=task_repo, permission_checker=permission_denied_stub)
        with pytest.raises(InsufficientTaskPermissionsException):
            await handler.handle(GetTasksByLabelsQuery(caller_id=str(Id.generate()), project_id=str(project_id), label_names=["backend"]))
