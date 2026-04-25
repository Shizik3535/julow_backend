"""Интеграционные тесты CreateTaskTemplateHandler (реальные repos + стабы портов)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.task.application.commands.create_task_template import CreateTaskTemplateCommand, CreateTaskTemplateHandler
from app.context.task.application.exceptions.authorization_exceptions import InsufficientTaskPermissionsException
from app.context.task.application.exceptions.task_template_app_exceptions import TaskTemplateAlreadyExistsException
from app.context.task.domain.value_objects.task_type import TaskType


@pytest.mark.integration
class TestCreateTaskTemplateHandler:
    """Тесты создания шаблона — full stack."""

    @pytest.fixture
    def handler(self, task_template_repo, permission_checker_stub, event_bus_stub) -> CreateTaskTemplateHandler:
        return CreateTaskTemplateHandler(template_repo=task_template_repo, permission_checker=permission_checker_stub, event_bus=event_bus_stub)

    async def test_create_template_success(self, handler, task_template_repo) -> None:
        project_id = Id.generate()
        cmd = CreateTaskTemplateCommand(
            caller_id=str(Id.generate()),
            project_id=str(project_id),
            name="Bug Template",
            task_type="bug",
        )
        result = await handler.handle(cmd)

        assert result.name == "Bug Template"
        assert result.task_type == "bug"
        assert result.is_system is False

        found = await task_template_repo.get_by_id(Id.from_string(result.id))
        assert found is not None
        assert found.task_type == TaskType.BUG

    async def test_create_custom_template_success(self, handler, task_template_repo, make_task_template) -> None:
        project_id = Id.generate()
        cmd = CreateTaskTemplateCommand(
            caller_id=str(Id.generate()),
            project_id=str(project_id),
            name="Custom Template",
            task_type="task",
        )
        result = await handler.handle(cmd)

        assert result.name == "Custom Template"
        assert result.is_system is False

        found = await task_template_repo.get_by_id(Id.from_string(result.id))
        assert found is not None
        assert found.project_id == project_id

    async def test_create_duplicate_template_raises(self, handler) -> None:
        project_id = Id.generate()
        cmd = CreateTaskTemplateCommand(
            caller_id=str(Id.generate()),
            project_id=str(project_id),
            name="Unique Template",
            task_type="task",
        )
        await handler.handle(cmd)

        with pytest.raises(TaskTemplateAlreadyExistsException):
            await handler.handle(cmd)

    async def test_create_template_permission_denied(self, task_template_repo, permission_denied_stub, event_bus_stub) -> None:
        handler = CreateTaskTemplateHandler(template_repo=task_template_repo, permission_checker=permission_denied_stub, event_bus=event_bus_stub)
        cmd = CreateTaskTemplateCommand(
            caller_id=str(Id.generate()),
            project_id=str(Id.generate()),
            name="Denied Template",
        )
        with pytest.raises(InsufficientTaskPermissionsException):
            await handler.handle(cmd)
