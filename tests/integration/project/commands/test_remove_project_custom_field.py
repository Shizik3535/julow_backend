"""Интеграционные тесты RemoveProjectCustomFieldHandler (реальные repos + реальные порты)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.project.application.commands.remove_project_custom_field import (
    RemoveProjectCustomFieldCommand,
    RemoveProjectCustomFieldHandler,
)
from app.context.project.domain.exceptions.project_exceptions import ProjectNotFoundException
from tests.integration.project.conftest import (
    _AlwaysAllowProjectPermissionChecker,
    _NoopEventBus,
)


@pytest.mark.integration
class TestRemoveProjectCustomFieldHandler:
    """Тесты RemoveProjectCustomFieldHandler."""

    @pytest.fixture
    def handler(self, project_repo, permission_checker_stub, event_bus_stub) -> RemoveProjectCustomFieldHandler:
        return RemoveProjectCustomFieldHandler(
            project_repo=project_repo,
            permission_checker=permission_checker_stub,
            event_bus=event_bus_stub,
        )

    async def test_remove_custom_field_success(self, handler, project_repo, make_project) -> None:
        from app.context.project.domain.value_objects.custom_field_definition import CustomFieldDefinition
        from app.context.project.domain.value_objects.custom_field_type import CustomFieldType

        project = await make_project()
        project.add_custom_field(CustomFieldDefinition(name="ToRemove", field_type=CustomFieldType.TEXT))
        project.clear_domain_events()
        await project_repo.update(project)

        cmd = RemoveProjectCustomFieldCommand(
            caller_id=str(Id.generate()),
            project_id=str(project.id),
            name="ToRemove",
        )
        await handler.handle(cmd)

        found = await project_repo.get_by_id(project.id)
        assert found is not None

    async def test_remove_custom_field_not_found(self, handler) -> None:
        cmd = RemoveProjectCustomFieldCommand(
            caller_id=str(Id.generate()),
            project_id=str(Id.generate()),
            name="X",
        )
        with pytest.raises(ProjectNotFoundException):
            await handler.handle(cmd)
