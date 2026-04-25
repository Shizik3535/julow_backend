"""Интеграционные тесты DeleteTaskTemplateHandler (реальные repos + стабы портов)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.task.application.commands.delete_task_template import DeleteTaskTemplateCommand, DeleteTaskTemplateHandler
from app.context.task.application.exceptions.authorization_exceptions import InsufficientTaskPermissionsException
from app.context.task.domain.exceptions.task_template_exceptions import (
    TaskTemplateNotFoundException,
    CannotDeleteSystemTemplateException,
)


@pytest.mark.integration
class TestDeleteTaskTemplateHandler:
    """Тесты удаления шаблона — full stack."""

    @pytest.fixture
    def handler(self, task_template_repo, permission_checker_stub, event_bus_stub) -> DeleteTaskTemplateHandler:
        return DeleteTaskTemplateHandler(template_repo=task_template_repo, permission_checker=permission_checker_stub, event_bus=event_bus_stub)

    async def test_delete_custom_template_success(self, handler, task_template_repo, make_task_template) -> None:
        template = await make_task_template()
        cmd = DeleteTaskTemplateCommand(caller_id=str(Id.generate()), template_id=str(template.id))
        await handler.handle(cmd)

        found = await task_template_repo.get_by_id(template.id)
        assert found is None

    async def test_delete_system_template_denied(self, handler, make_task_template) -> None:
        template = await make_task_template(is_system=True)
        cmd = DeleteTaskTemplateCommand(caller_id=str(Id.generate()), template_id=str(template.id))
        with pytest.raises(CannotDeleteSystemTemplateException):
            await handler.handle(cmd)

    async def test_delete_project_template_permission_denied(self, task_template_repo, permission_denied_stub, event_bus_stub, make_task_template) -> None:
        project_id = Id.generate()
        template = await make_task_template(project_id=project_id)
        handler = DeleteTaskTemplateHandler(template_repo=task_template_repo, permission_checker=permission_denied_stub, event_bus=event_bus_stub)
        cmd = DeleteTaskTemplateCommand(caller_id=str(Id.generate()), template_id=str(template.id))
        with pytest.raises(InsufficientTaskPermissionsException):
            await handler.handle(cmd)

    async def test_delete_system_template_no_permission_check(self, task_template_repo, permission_denied_stub, event_bus_stub, make_task_template) -> None:
        template = await make_task_template(is_system=True)
        handler = DeleteTaskTemplateHandler(template_repo=task_template_repo, permission_checker=permission_denied_stub, event_bus=event_bus_stub)
        cmd = DeleteTaskTemplateCommand(caller_id=str(Id.generate()), template_id=str(template.id))
        with pytest.raises(CannotDeleteSystemTemplateException):
            await handler.handle(cmd)

    async def test_delete_template_not_found(self, handler) -> None:
        cmd = DeleteTaskTemplateCommand(caller_id=str(Id.generate()), template_id=str(Id.generate()))
        with pytest.raises(TaskTemplateNotFoundException):
            await handler.handle(cmd)
