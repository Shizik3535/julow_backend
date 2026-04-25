"""Интеграционные тесты GetTaskTemplateHandler (реальные repos + стабы портов)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.task.application.queries.get_task_template import GetTaskTemplateQuery, GetTaskTemplateHandler
from app.context.task.application.exceptions.authorization_exceptions import InsufficientTaskPermissionsException
from app.context.task.domain.exceptions.task_template_exceptions import TaskTemplateNotFoundException


@pytest.mark.integration
class TestGetTaskTemplateHandler:
    """Тесты получения шаблона по ID — full stack."""

    @pytest.fixture
    def handler(self, task_template_repo, permission_checker_stub) -> GetTaskTemplateHandler:
        return GetTaskTemplateHandler(template_repo=task_template_repo, permission_checker=permission_checker_stub)

    async def test_get_template_found(self, handler, make_task_template) -> None:
        template = await make_task_template(name="My Template")
        result = await handler.handle(GetTaskTemplateQuery(caller_id=str(Id.generate()), template_id=str(template.id)))
        assert result.name == "My Template"

    async def test_get_template_not_found(self, handler) -> None:
        with pytest.raises(TaskTemplateNotFoundException):
            await handler.handle(GetTaskTemplateQuery(caller_id=str(Id.generate()), template_id=str(Id.generate())))

    async def test_get_project_template_permission_denied(self, task_template_repo, permission_denied_stub, make_task_template) -> None:
        project_id = Id.generate()
        template = await make_task_template(project_id=project_id)
        handler = GetTaskTemplateHandler(template_repo=task_template_repo, permission_checker=permission_denied_stub)
        with pytest.raises(InsufficientTaskPermissionsException):
            await handler.handle(GetTaskTemplateQuery(caller_id=str(Id.generate()), template_id=str(template.id)))

    async def test_get_system_template_no_permission_check(self, task_template_repo, permission_denied_stub, make_task_template) -> None:
        template = await make_task_template(is_system=True)
        handler = GetTaskTemplateHandler(template_repo=task_template_repo, permission_checker=permission_denied_stub)
        result = await handler.handle(GetTaskTemplateQuery(caller_id=str(Id.generate()), template_id=str(template.id)))
        assert result is not None
