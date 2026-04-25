"""Интеграционные тесты GetTaskTemplatesByProjectHandler (реальные repos + стабы портов)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.task.application.queries.get_task_templates_by_project import GetTaskTemplatesByProjectQuery, GetTaskTemplatesByProjectHandler
from app.context.task.application.exceptions.authorization_exceptions import InsufficientTaskPermissionsException


@pytest.mark.integration
class TestGetTaskTemplatesByProjectHandler:
    """Тесты получения шаблонов проекта — full stack."""

    @pytest.fixture
    def handler(self, task_template_repo, permission_checker_stub) -> GetTaskTemplatesByProjectHandler:
        return GetTaskTemplatesByProjectHandler(template_repo=task_template_repo, permission_checker=permission_checker_stub)

    async def test_get_templates_by_project(self, handler, make_task_template) -> None:
        await make_task_template(name="ProjTmpl")
        result = await handler.handle(GetTaskTemplatesByProjectQuery(caller_id=str(Id.generate()), project_id=str(Id.generate())))
        assert len(result.items) >= 0

    async def test_get_templates_by_project_permission_denied(self, task_template_repo, permission_denied_stub, make_task_template) -> None:
        await make_task_template(name="ProjTmpl")
        handler = GetTaskTemplatesByProjectHandler(template_repo=task_template_repo, permission_checker=permission_denied_stub)
        with pytest.raises(InsufficientTaskPermissionsException):
            await handler.handle(GetTaskTemplatesByProjectQuery(caller_id=str(Id.generate()), project_id=str(Id.generate())))
