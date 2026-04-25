"""Интеграционные тесты SetTaskCustomFieldHandler (реальные repos + стабы портов)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.task.application.commands.set_task_custom_field import SetTaskCustomFieldCommand, SetTaskCustomFieldHandler
from app.context.task.application.exceptions.authorization_exceptions import InsufficientTaskPermissionsException
from app.context.task.domain.exceptions.task_exceptions import TaskNotFoundException


@pytest.mark.integration
class TestSetTaskCustomFieldHandler:
    """Тесты установки кастомного поля — full stack."""

    @pytest.fixture
    def handler(self, task_repo, changelog_repo, project_stub, permission_checker_stub, event_bus_stub) -> SetTaskCustomFieldHandler:
        return SetTaskCustomFieldHandler(
            task_repo=task_repo,
            changelog_repo=changelog_repo,
            project_port=project_stub,
            permission_checker=permission_checker_stub,
            event_bus=event_bus_stub,
        )

    async def test_set_custom_field_success(self, handler, task_repo, make_task) -> None:
        task = await make_task()
        cmd = SetTaskCustomFieldCommand(
            caller_id=str(Id.generate()),
            task_id=str(task.id),
            field_name="priority_level",
            value="P1",
            changed_by=str(Id.generate()),
        )
        await handler.handle(cmd)

        found = await task_repo.get_by_id(task.id)
        assert found is not None
        assert found.custom_fields.get("priority_level") == "P1"

    async def test_set_custom_field_creates_changelog(self, handler, changelog_repo, make_task) -> None:
        task = await make_task()
        cmd = SetTaskCustomFieldCommand(
            caller_id=str(Id.generate()),
            task_id=str(task.id),
            field_name="team",
            value="backend",
            changed_by=str(Id.generate()),
        )
        await handler.handle(cmd)

        entries = await changelog_repo.get_by_task_and_field(task.id, "custom_field:team")
        assert len(entries) >= 1

    async def test_set_custom_field_task_not_found(self, handler) -> None:
        cmd = SetTaskCustomFieldCommand(
            caller_id=str(Id.generate()),
            task_id=str(Id.generate()),
            field_name="field",
            value="val",
            changed_by=str(Id.generate()),
        )
        with pytest.raises(TaskNotFoundException):
            await handler.handle(cmd)

    async def test_set_custom_field_permission_denied(self, task_repo, changelog_repo, project_stub, permission_denied_stub, event_bus_stub, make_task) -> None:
        task = await make_task()
        handler = SetTaskCustomFieldHandler(
            task_repo=task_repo,
            changelog_repo=changelog_repo,
            project_port=project_stub,
            permission_checker=permission_denied_stub,
            event_bus=event_bus_stub,
        )
        cmd = SetTaskCustomFieldCommand(
            caller_id=str(Id.generate()),
            task_id=str(task.id),
            field_name="field",
            value="val",
            changed_by=str(Id.generate()),
        )
        with pytest.raises(InsufficientTaskPermissionsException):
            await handler.handle(cmd)
