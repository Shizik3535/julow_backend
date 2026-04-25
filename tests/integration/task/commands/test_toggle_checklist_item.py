"""Интеграционные тесты ToggleChecklistItemHandler (реальные repos + стабы портов)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.task.application.commands.toggle_checklist_item import ToggleChecklistItemCommand, ToggleChecklistItemHandler
from app.context.task.application.exceptions.authorization_exceptions import InsufficientTaskPermissionsException
from app.context.task.domain.exceptions.task_exceptions import TaskNotFoundException


@pytest.mark.integration
class TestToggleChecklistItemHandler:
    """Тесты отметки/снятия пункта чек-листа — full stack."""

    @pytest.fixture
    def handler(self, task_repo, permission_checker_stub, event_bus_stub) -> ToggleChecklistItemHandler:
        return ToggleChecklistItemHandler(task_repo=task_repo, permission_checker=permission_checker_stub, event_bus=event_bus_stub)

    async def test_toggle_check_item_success(self, handler, task_repo, make_task) -> None:
        task = await make_task()
        cl = task.add_checklist("List")
        task.add_checklist_item(cl.id, "Item 1")
        item_id = cl.items[0].id
        task.clear_domain_events()
        await task_repo.update(task)

        cmd = ToggleChecklistItemCommand(
            caller_id=str(Id.generate()),
            task_id=str(task.id),
            checklist_id=str(cl.id),
            item_id=str(item_id),
        )
        await handler.handle(cmd)

        found = await task_repo.get_by_id(task.id)
        assert found is not None
        assert found.checklists[0].items[0].is_checked is True

    async def test_toggle_uncheck_item(self, handler, task_repo, make_task) -> None:
        task = await make_task()
        cl = task.add_checklist("List")
        task.add_checklist_item(cl.id, "Item 1")
        item_id = cl.items[0].id
        task.clear_domain_events()
        await task_repo.update(task)

        cmd = ToggleChecklistItemCommand(
            caller_id=str(Id.generate()),
            task_id=str(task.id),
            checklist_id=str(cl.id),
            item_id=str(item_id),
        )
        await handler.handle(cmd)
        await handler.handle(cmd)

        found = await task_repo.get_by_id(task.id)
        assert found is not None
        assert found.checklists[0].items[0].is_checked is False

    async def test_toggle_checklist_item_task_not_found(self, handler) -> None:
        cmd = ToggleChecklistItemCommand(
            caller_id=str(Id.generate()),
            task_id=str(Id.generate()),
            checklist_id=str(Id.generate()),
            item_id=str(Id.generate()),
        )
        with pytest.raises(TaskNotFoundException):
            await handler.handle(cmd)

    async def test_toggle_checklist_item_permission_denied(self, task_repo, permission_denied_stub, event_bus_stub, make_task) -> None:
        task = await make_task()
        handler = ToggleChecklistItemHandler(task_repo=task_repo, permission_checker=permission_denied_stub, event_bus=event_bus_stub)
        cmd = ToggleChecklistItemCommand(
            caller_id=str(Id.generate()),
            task_id=str(task.id),
            checklist_id=str(Id.generate()),
            item_id=str(Id.generate()),
        )
        with pytest.raises(InsufficientTaskPermissionsException):
            await handler.handle(cmd)
