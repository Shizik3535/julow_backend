"""Интеграционные тесты AddChecklistHandler (реальные repos + стабы портов)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.task.application.commands.add_checklist import AddChecklistCommand, AddChecklistHandler
from app.context.task.application.exceptions.authorization_exceptions import InsufficientTaskPermissionsException
from app.context.task.domain.exceptions.task_exceptions import TaskNotFoundException


@pytest.mark.integration
class TestAddChecklistHandler:
    """Тесты добавления чек-листа — full stack."""

    @pytest.fixture
    def handler(self, task_repo, permission_checker_stub, event_bus_stub) -> AddChecklistHandler:
        return AddChecklistHandler(task_repo=task_repo, permission_checker=permission_checker_stub, event_bus=event_bus_stub)

    async def test_add_checklist_success(self, handler, task_repo, make_task) -> None:
        task = await make_task()
        cmd = AddChecklistCommand(
            caller_id=str(Id.generate()),
            task_id=str(task.id),
            title="My List",
        )
        checklist_id = await handler.handle(cmd)

        found = await task_repo.get_by_id(task.id)
        assert found is not None
        assert len(found.checklists) == 1
        assert found.checklists[0].title == "My List"
        assert str(found.checklists[0].id) == checklist_id

    async def test_add_checklist_task_not_found(self, handler) -> None:
        cmd = AddChecklistCommand(
            caller_id=str(Id.generate()),
            task_id=str(Id.generate()),
            title="List",
        )
        with pytest.raises(TaskNotFoundException):
            await handler.handle(cmd)

    async def test_add_checklist_permission_denied(self, task_repo, permission_denied_stub, event_bus_stub, make_task) -> None:
        task = await make_task()
        handler = AddChecklistHandler(task_repo=task_repo, permission_checker=permission_denied_stub, event_bus=event_bus_stub)
        cmd = AddChecklistCommand(
            caller_id=str(Id.generate()),
            task_id=str(task.id),
            title="Denied",
        )
        with pytest.raises(InsufficientTaskPermissionsException):
            await handler.handle(cmd)
