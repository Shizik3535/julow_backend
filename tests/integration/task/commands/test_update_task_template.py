"""Интеграционные тесты UpdateTaskTemplateHandler (реальные repos + стабы портов)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.task.application.commands.update_task_template import UpdateTaskTemplateCommand, UpdateTaskTemplateHandler
from app.context.task.application.exceptions.authorization_exceptions import InsufficientTaskPermissionsException
from app.context.task.domain.exceptions.task_template_exceptions import TaskTemplateNotFoundException


@pytest.mark.integration
class TestUpdateTaskTemplateHandler:
    """Тесты обновления шаблона — full stack."""

    @pytest.fixture
    def handler(self, task_template_repo, permission_checker_stub, event_bus_stub) -> UpdateTaskTemplateHandler:
        return UpdateTaskTemplateHandler(template_repo=task_template_repo, permission_checker=permission_checker_stub, event_bus=event_bus_stub)

    async def test_update_labels_success(self, handler, task_template_repo, make_task_template) -> None:
        template = await make_task_template()
        cmd = UpdateTaskTemplateCommand(
            caller_id=str(Id.generate()),
            template_id=str(template.id),
            default_labels=[{"name": "updated"}],
        )
        await handler.handle(cmd)

        found = await task_template_repo.get_by_id(template.id)
        assert found is not None
        assert len(found.default_labels) == 1
        assert found.default_labels[0].name == "updated"

    async def test_update_custom_fields_success(self, handler, task_template_repo, make_task_template) -> None:
        template = await make_task_template()
        cmd = UpdateTaskTemplateCommand(
            caller_id=str(Id.generate()),
            template_id=str(template.id),
            default_custom_fields={"team": "backend"},
        )
        await handler.handle(cmd)

        found = await task_template_repo.get_by_id(template.id)
        assert found is not None
        assert found.default_custom_fields == {"team": "backend"}

    async def test_update_template_not_found(self, handler) -> None:
        cmd = UpdateTaskTemplateCommand(caller_id=str(Id.generate()), template_id=str(Id.generate()))
        with pytest.raises(TaskTemplateNotFoundException):
            await handler.handle(cmd)

    async def test_update_project_template_permission_denied(self, task_template_repo, permission_denied_stub, event_bus_stub, make_task_template) -> None:
        project_id = Id.generate()
        template = await make_task_template(project_id=project_id)
        handler = UpdateTaskTemplateHandler(template_repo=task_template_repo, permission_checker=permission_denied_stub, event_bus=event_bus_stub)
        cmd = UpdateTaskTemplateCommand(caller_id=str(Id.generate()), template_id=str(template.id))
        with pytest.raises(InsufficientTaskPermissionsException):
            await handler.handle(cmd)

    async def test_update_system_template_no_permission_check(self, task_template_repo, permission_denied_stub, event_bus_stub, make_task_template) -> None:
        template = await make_task_template(is_system=True)
        handler = UpdateTaskTemplateHandler(template_repo=task_template_repo, permission_checker=permission_denied_stub, event_bus=event_bus_stub)
        cmd = UpdateTaskTemplateCommand(caller_id=str(Id.generate()), template_id=str(template.id))
        # System templates have no project_id, so no permission check — should succeed
        await handler.handle(cmd)
