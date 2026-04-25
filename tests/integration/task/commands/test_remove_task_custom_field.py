"""Интеграционные тесты RemoveTaskCustomFieldHandler (реальные repos + стабы портов)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.task.application.commands.remove_task_custom_field import RemoveTaskCustomFieldCommand, RemoveTaskCustomFieldHandler
from app.context.task.application.exceptions.authorization_exceptions import InsufficientTaskPermissionsException
from app.context.task.domain.exceptions.task_exceptions import TaskNotFoundException


@pytest.mark.integration
class TestRemoveTaskCustomFieldHandler:
    """Тесты удаления кастомного поля — full stack."""

    @pytest.fixture
    def handler(self, task_repo, changelog_repo, permission_checker_stub, event_bus_stub) -> RemoveTaskCustomFieldHandler:
        return RemoveTaskCustomFieldHandler(
            task_repo=task_repo,
            changelog_repo=changelog_repo,
            permission_checker=permission_checker_stub,
            event_bus=event_bus_stub,
        )

    async def test_remove_custom_field_success(self, handler, task_repo, make_task) -> None:
        task = await make_task()
        task.set_custom_field("team", "backend")
        task.clear_domain_events()
        await task_repo.update(task)

        cmd = RemoveTaskCustomFieldCommand(
            caller_id=str(Id.generate()),
            task_id=str(task.id),
            field_name="team",
            changed_by=str(Id.generate()),
        )
        await handler.handle(cmd)

        found = await task_repo.get_by_id(task.id)
        assert found is not None
        assert "team" not in found.custom_fields

    async def test_remove_custom_field_creates_changelog(self, handler, changelog_repo, make_task) -> None:
        task = await make_task()
        task.set_custom_field("env", "prod")
        task.clear_domain_events()
        await handler._task_repo.update(task)

        cmd = RemoveTaskCustomFieldCommand(
            caller_id=str(Id.generate()),
            task_id=str(task.id),
            field_name="env",
            changed_by=str(Id.generate()),
        )
        await handler.handle(cmd)

        entries = await changelog_repo.get_by_task_and_field(task.id, "custom_field:env")
        assert len(entries) >= 1

    async def test_remove_custom_field_task_not_found(self, handler) -> None:
        cmd = RemoveTaskCustomFieldCommand(
            caller_id=str(Id.generate()),
            task_id=str(Id.generate()),
            field_name="priority",
            changed_by=str(Id.generate()),
        )
        with pytest.raises(TaskNotFoundException):
            await handler.handle(cmd)

    async def test_remove_custom_field_permission_denied(self, task_repo, changelog_repo, permission_denied_stub, event_bus_stub, make_task) -> None:
        task = await make_task()
        handler = RemoveTaskCustomFieldHandler(task_repo=task_repo, changelog_repo=changelog_repo, permission_checker=permission_denied_stub, event_bus=event_bus_stub)
        cmd = RemoveTaskCustomFieldCommand(
            caller_id=str(Id.generate()),
            task_id=str(task.id),
            field_name="priority",
            changed_by=str(Id.generate()),
        )
        with pytest.raises(InsufficientTaskPermissionsException):
            await handler.handle(cmd)
