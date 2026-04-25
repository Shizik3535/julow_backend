"""Интеграционные тесты AssignChecklistItemHandler (реальные repos + стабы портов)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.task.application.commands.assign_checklist_item import AssignChecklistItemCommand, AssignChecklistItemHandler
from app.context.task.application.exceptions.authorization_exceptions import InsufficientTaskPermissionsException
from app.context.task.domain.exceptions.task_exceptions import TaskNotFoundException


@pytest.mark.integration
class TestAssignChecklistItemHandler:
    """Тесты назначения исполнителя на пункт чек-листа — full stack."""

    @pytest.fixture
    def handler(self, task_repo, permission_checker_stub, event_bus_stub) -> AssignChecklistItemHandler:
        return AssignChecklistItemHandler(task_repo=task_repo, permission_checker=permission_checker_stub, event_bus=event_bus_stub)

    async def test_assign_checklist_item_success(self, handler, task_repo, make_task) -> None:
        task = await make_task()
        cl = task.add_checklist("List")
        task.add_checklist_item(cl.id, "Item 1")
        item_id = cl.items[0].id
        task.clear_domain_events()
        await task_repo.update(task)

        assignee_id = Id.generate()
        cmd = AssignChecklistItemCommand(
            caller_id=str(Id.generate()),
            task_id=str(task.id),
            checklist_id=str(cl.id),
            item_id=str(item_id),
            assignee_id=str(assignee_id),
        )
        await handler.handle(cmd)

        found = await task_repo.get_by_id(task.id)
        assert found is not None
        assert found.checklists[0].items[0].assignee_id == assignee_id

    async def test_assign_checklist_item_task_not_found(self, handler) -> None:
        cmd = AssignChecklistItemCommand(
            caller_id=str(Id.generate()),
            task_id=str(Id.generate()),
            checklist_id=str(Id.generate()),
            item_id=str(Id.generate()),
            assignee_id=str(Id.generate()),
        )
        with pytest.raises(TaskNotFoundException):
            await handler.handle(cmd)

    async def test_assign_checklist_item_permission_denied(self, task_repo, permission_denied_stub, event_bus_stub, make_task) -> None:
        task = await make_task()
        cl = task.add_checklist("List")
        task.add_checklist_item(cl.id, "Item 1")
        item_id = cl.items[0].id
        task.clear_domain_events()
        await task_repo.update(task)
        handler = AssignChecklistItemHandler(task_repo=task_repo, permission_checker=permission_denied_stub, event_bus=event_bus_stub)
        cmd = AssignChecklistItemCommand(
            caller_id=str(Id.generate()),
            task_id=str(task.id),
            checklist_id=str(cl.id),
            item_id=str(item_id),
            assignee_id=str(Id.generate()),
        )
        with pytest.raises(InsufficientTaskPermissionsException):
            await handler.handle(cmd)
