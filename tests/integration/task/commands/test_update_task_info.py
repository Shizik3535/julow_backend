"""Интеграционные тесты UpdateTaskInfoHandler (реальные repos + стабы портов)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.task.application.commands.update_task_info import UpdateTaskInfoCommand, UpdateTaskInfoHandler
from app.context.task.application.exceptions.authorization_exceptions import InsufficientTaskPermissionsException
from app.context.task.domain.exceptions.task_exceptions import TaskNotFoundException


@pytest.mark.integration
class TestUpdateTaskInfoHandler:
    """Тесты обновления информации задачи — full stack."""

    @pytest.fixture
    def handler(self, task_repo, changelog_repo, permission_checker_stub, event_bus_stub) -> UpdateTaskInfoHandler:
        return UpdateTaskInfoHandler(
            task_repo=task_repo,
            changelog_repo=changelog_repo,
            permission_checker=permission_checker_stub,
            event_bus=event_bus_stub,
        )

    async def test_update_title_success(self, handler, task_repo, make_task) -> None:
        task = await make_task()
        changed_by = Id.generate()

        cmd = UpdateTaskInfoCommand(
            task_id=str(task.id),
            changed_by=str(changed_by),
            title="Updated Title",
        )
        await handler.handle(cmd)

        found = await task_repo.get_by_id(task.id)
        assert found is not None
        assert found.title == "Updated Title"

    async def test_update_due_date_success(self, handler, task_repo, make_task) -> None:
        task = await make_task()
        changed_by = Id.generate()

        cmd = UpdateTaskInfoCommand(
            task_id=str(task.id),
            changed_by=str(changed_by),
            due_date="2026-12-31",
        )
        await handler.handle(cmd)

        found = await task_repo.get_by_id(task.id)
        assert found is not None
        assert found.due_date is not None

    async def test_update_creates_changelog(self, handler, changelog_repo, make_task) -> None:
        task = await make_task()
        changed_by = Id.generate()

        cmd = UpdateTaskInfoCommand(
            task_id=str(task.id),
            changed_by=str(changed_by),
            title="New Title",
        )
        await handler.handle(cmd)

        entries = await changelog_repo.get_by_task_and_field(task.id, "title")
        assert len(entries) >= 1

    async def test_update_task_not_found(self, handler) -> None:
        cmd = UpdateTaskInfoCommand(
            task_id=str(Id.generate()),
            changed_by=str(Id.generate()),
            title="Nothing",
        )
        with pytest.raises(TaskNotFoundException):
            await handler.handle(cmd)

    async def test_update_task_info_permission_denied(self, task_repo, changelog_repo, permission_denied_stub, event_bus_stub, make_task) -> None:
        task = await make_task()
        handler = UpdateTaskInfoHandler(
            task_repo=task_repo,
            changelog_repo=changelog_repo,
            permission_checker=permission_denied_stub,
            event_bus=event_bus_stub,
        )
        cmd = UpdateTaskInfoCommand(
            task_id=str(task.id),
            changed_by=str(Id.generate()),
            title="Denied",
        )
        with pytest.raises(InsufficientTaskPermissionsException):
            await handler.handle(cmd)
