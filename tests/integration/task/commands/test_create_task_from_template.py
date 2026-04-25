"""Интеграционные тесты CreateTaskFromTemplateHandler (реальные repos + стабы портов)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.task.application.commands.create_task_from_template import CreateTaskFromTemplateCommand, CreateTaskFromTemplateHandler
from app.context.task.application.exceptions.authorization_exceptions import InsufficientTaskPermissionsException
from app.context.task.application.exceptions.task_app_exceptions import TaskProjectNotFoundException
from app.context.task.domain.exceptions.task_template_exceptions import TaskTemplateNotFoundException
from app.context.task.domain.value_objects.task_type import TaskType


@pytest.mark.integration
class TestCreateTaskFromTemplateHandler:
    """Тесты создания задачи из шаблона — full stack."""

    @pytest.fixture
    def handler(self, task_repo, task_template_repo, project_stub, board_stub, permission_checker_stub, event_bus_stub) -> CreateTaskFromTemplateHandler:
        return CreateTaskFromTemplateHandler(
            task_repo=task_repo,
            template_repo=task_template_repo,
            project_port=project_stub,
            board_port=board_stub,
            permission_checker=permission_checker_stub,
            event_bus=event_bus_stub,
        )

    async def test_create_from_template_success(self, handler, task_repo, make_task_template) -> None:
        template = await make_task_template(name="Bug Template", task_type=TaskType.BUG)
        project_id = Id.generate()
        reporter_id = Id.generate()

        cmd = CreateTaskFromTemplateCommand(
            caller_id=str(reporter_id),
            project_id=str(project_id),
            template_id=str(template.id),
            reporter_id=str(reporter_id),
        )
        result = await handler.handle(cmd)

        assert result.title == "Bug Template"
        assert result.task_type == "bug"

        found = await task_repo.get_by_id(Id.from_string(result.id))
        assert found is not None
        assert found.task_type == TaskType.BUG

    async def test_create_from_template_project_not_found(self, handler, make_task_template) -> None:
        template = await make_task_template()

        class _NotFoundProject(handler._project_port.__class__):
            async def project_exists(self, project_id: str) -> bool:
                return False

        handler._project_port = _NotFoundProject()

        cmd = CreateTaskFromTemplateCommand(
            caller_id=str(Id.generate()),
            project_id=str(Id.generate()),
            template_id=str(template.id),
            reporter_id=str(Id.generate()),
        )
        with pytest.raises(TaskProjectNotFoundException):
            await handler.handle(cmd)

    async def test_create_from_template_not_found(self, handler) -> None:
        cmd = CreateTaskFromTemplateCommand(
            caller_id=str(Id.generate()),
            project_id=str(Id.generate()),
            template_id=str(Id.generate()),
            reporter_id=str(Id.generate()),
        )
        with pytest.raises(TaskTemplateNotFoundException):
            await handler.handle(cmd)

    async def test_create_from_template_permission_denied(self, task_repo, task_template_repo, project_stub, board_stub, permission_denied_stub, event_bus_stub, make_task_template) -> None:
        template = await make_task_template(name="Bug Template", task_type=TaskType.BUG)
        handler = CreateTaskFromTemplateHandler(
            task_repo=task_repo,
            template_repo=task_template_repo,
            project_port=project_stub,
            board_port=board_stub,
            permission_checker=permission_denied_stub,
            event_bus=event_bus_stub,
        )
        cmd = CreateTaskFromTemplateCommand(
            caller_id=str(Id.generate()),
            project_id=str(Id.generate()),
            template_id=str(template.id),
            reporter_id=str(Id.generate()),
        )
        with pytest.raises(InsufficientTaskPermissionsException):
            await handler.handle(cmd)
