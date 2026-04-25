"""Интеграционные тесты AddChecklistItemHandler (реальные repos + стабы портов)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.task.application.commands.add_checklist_item import AddChecklistItemCommand, AddChecklistItemHandler
from app.context.task.application.exceptions.authorization_exceptions import InsufficientTaskPermissionsException
from app.context.task.domain.exceptions.task_exceptions import TaskNotFoundException, ChecklistNotFoundException


@pytest.mark.integration
class TestAddChecklistItemHandler:
    """Тесты добавления пункта чек-листа — full stack."""

    @pytest.fixture
    def handler(self, task_repo, permission_checker_stub, event_bus_stub) -> AddChecklistItemHandler:
        return AddChecklistItemHandler(task_repo=task_repo, permission_checker=permission_checker_stub, event_bus=event_bus_stub)

    async def test_add_checklist_item_success(self, handler, task_repo, make_task) -> None:
        task = await make_task()
        cl = task.add_checklist("My List")
        task.clear_domain_events()
        await task_repo.update(task)

        cmd = AddChecklistItemCommand(
            caller_id=str(Id.generate()),
            task_id=str(task.id),
            checklist_id=str(cl.id),
            text="Item 1",
        )
        await handler.handle(cmd)

        found = await task_repo.get_by_id(task.id)
        assert found is not None
        assert len(found.checklists[0].items) == 1
        assert found.checklists[0].items[0].text == "Item 1"

    async def test_add_checklist_item_task_not_found(self, handler) -> None:
        cmd = AddChecklistItemCommand(
            caller_id=str(Id.generate()),
            task_id=str(Id.generate()),
            checklist_id=str(Id.generate()),
            text="Item",
        )
        with pytest.raises(TaskNotFoundException):
            await handler.handle(cmd)

    async def test_add_checklist_item_checklist_not_found(self, handler, make_task) -> None:
        task = await make_task()
        cmd = AddChecklistItemCommand(
            caller_id=str(Id.generate()),
            task_id=str(task.id),
            checklist_id=str(Id.generate()),
            text="Item",
        )
        with pytest.raises(ChecklistNotFoundException):
            await handler.handle(cmd)

    async def test_add_checklist_item_permission_denied(self, task_repo, permission_denied_stub, event_bus_stub, make_task) -> None:
        task = await make_task()
        handler = AddChecklistItemHandler(task_repo=task_repo, permission_checker=permission_denied_stub, event_bus=event_bus_stub)
        cmd = AddChecklistItemCommand(
            caller_id=str(Id.generate()),
            task_id=str(task.id),
            checklist_id=str(Id.generate()),
            text="Denied",
        )
        with pytest.raises(InsufficientTaskPermissionsException):
            await handler.handle(cmd)
