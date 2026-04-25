"""Интеграционные тесты AddTaskRelationHandler (реальные repos + стабы портов)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.task.application.commands.add_task_relation import AddTaskRelationCommand, AddTaskRelationHandler
from app.context.task.application.exceptions.authorization_exceptions import InsufficientTaskPermissionsException
from app.context.task.domain.exceptions.task_exceptions import TaskNotFoundException
from app.context.task.domain.value_objects.relation_type import RelationType


@pytest.mark.integration
class TestAddTaskRelationHandler:
    """Тесты добавления связи между задачами — full stack."""

    @pytest.fixture
    def handler(self, task_repo, permission_checker_stub, event_bus_stub) -> AddTaskRelationHandler:
        return AddTaskRelationHandler(task_repo=task_repo, permission_checker=permission_checker_stub, event_bus=event_bus_stub)

    async def test_add_relation_success(self, handler, task_repo, make_task) -> None:
        task = await make_task()
        related = await make_task()
        created_by = Id.generate()

        cmd = AddTaskRelationCommand(
            caller_id=str(Id.generate()),
            task_id=str(task.id),
            related_task_id=str(related.id),
            relation_type="relates_to",
            created_by=str(created_by),
        )
        await handler.handle(cmd)

        found = await task_repo.get_by_id(task.id)
        assert found is not None
        assert len(found.relations) == 1
        assert found.relations[0].related_task_id == related.id
        assert found.relations[0].relation_type == RelationType.RELATES_TO

    async def test_add_relation_task_not_found(self, handler, make_task) -> None:
        task = await make_task()
        cmd = AddTaskRelationCommand(
            caller_id=str(Id.generate()),
            task_id=str(Id.generate()),
            related_task_id=str(task.id),
            relation_type="relates_to",
            created_by=str(Id.generate()),
        )
        with pytest.raises(TaskNotFoundException):
            await handler.handle(cmd)

    async def test_add_relation_related_task_not_found(self, handler, make_task) -> None:
        task = await make_task()
        cmd = AddTaskRelationCommand(
            caller_id=str(Id.generate()),
            task_id=str(task.id),
            related_task_id=str(Id.generate()),
            relation_type="relates_to",
            created_by=str(Id.generate()),
        )
        with pytest.raises(TaskNotFoundException):
            await handler.handle(cmd)

    async def test_add_relation_permission_denied(self, task_repo, permission_denied_stub, event_bus_stub, make_task) -> None:
        task = await make_task()
        related = await make_task()
        handler = AddTaskRelationHandler(task_repo=task_repo, permission_checker=permission_denied_stub, event_bus=event_bus_stub)
        cmd = AddTaskRelationCommand(
            caller_id=str(Id.generate()),
            task_id=str(task.id),
            related_task_id=str(related.id),
            relation_type="relates_to",
            created_by=str(Id.generate()),
        )
        with pytest.raises(InsufficientTaskPermissionsException):
            await handler.handle(cmd)
