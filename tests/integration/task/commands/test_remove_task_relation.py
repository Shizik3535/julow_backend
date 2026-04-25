"""Интеграционные тесты RemoveTaskRelationHandler (реальные repos + стабы портов)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.task.application.commands.remove_task_relation import RemoveTaskRelationCommand, RemoveTaskRelationHandler
from app.context.task.application.exceptions.authorization_exceptions import InsufficientTaskPermissionsException
from app.context.task.domain.exceptions.task_exceptions import TaskNotFoundException
from app.context.task.domain.value_objects.relation_type import RelationType


@pytest.mark.integration
class TestRemoveTaskRelationHandler:
    """Тесты удаления связи между задачами — full stack."""

    @pytest.fixture
    def handler(self, task_repo, permission_checker_stub, event_bus_stub) -> RemoveTaskRelationHandler:
        return RemoveTaskRelationHandler(task_repo=task_repo, permission_checker=permission_checker_stub, event_bus=event_bus_stub)

    async def test_remove_relation_success(self, handler, task_repo, make_task) -> None:
        task = await make_task()
        related_id = Id.generate()
        created_by = Id.generate()
        task.add_relation(related_id, RelationType.RELATES_TO, created_by)
        task.clear_domain_events()
        await task_repo.update(task)

        cmd = RemoveTaskRelationCommand(
            caller_id=str(Id.generate()),
            task_id=str(task.id),
            related_task_id=str(related_id),
            relation_type="relates_to",
        )
        await handler.handle(cmd)

        found = await task_repo.get_by_id(task.id)
        assert found is not None
        assert len(found.relations) == 0

    async def test_remove_relation_task_not_found(self, handler) -> None:
        cmd = RemoveTaskRelationCommand(
            caller_id=str(Id.generate()),
            task_id=str(Id.generate()),
            related_task_id=str(Id.generate()),
            relation_type="relates_to",
        )
        with pytest.raises(TaskNotFoundException):
            await handler.handle(cmd)

    async def test_remove_relation_permission_denied(self, task_repo, permission_denied_stub, event_bus_stub, make_task) -> None:
        task = await make_task()
        handler = RemoveTaskRelationHandler(task_repo=task_repo, permission_checker=permission_denied_stub, event_bus=event_bus_stub)
        cmd = RemoveTaskRelationCommand(
            caller_id=str(Id.generate()),
            task_id=str(task.id),
            related_task_id=str(Id.generate()),
            relation_type="relates_to",
        )
        with pytest.raises(InsufficientTaskPermissionsException):
            await handler.handle(cmd)
