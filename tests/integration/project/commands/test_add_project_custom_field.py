"""Интеграционные тесты AddProjectCustomFieldHandler (реальные repos + реальные порты)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.project.application.commands.add_project_custom_field import (
    AddProjectCustomFieldCommand,
    AddProjectCustomFieldHandler,
)
from app.context.project.domain.exceptions.project_exceptions import ProjectNotFoundException
from tests.integration.project.conftest import (
    _AlwaysAllowProjectPermissionChecker,
    _NoopEventBus,
)


@pytest.mark.integration
class TestAddProjectCustomFieldHandler:
    """Тесты AddProjectCustomFieldHandler."""

    @pytest.fixture
    def handler(self, project_repo, permission_checker_stub, event_bus_stub) -> AddProjectCustomFieldHandler:
        return AddProjectCustomFieldHandler(
            project_repo=project_repo,
            permission_checker=permission_checker_stub,
            event_bus=event_bus_stub,
        )

    async def test_add_custom_field_success(self, handler, project_repo, make_project) -> None:
        project = await make_project()
        cmd = AddProjectCustomFieldCommand(
            caller_id=str(Id.generate()),
            project_id=str(project.id),
            name="Priority",
            field_type="select",
            options=["Low", "Medium", "High"],
        )
        await handler.handle(cmd)

        found = await project_repo.get_by_id(project.id)
        assert found is not None
        assert any(f.name == "Priority" for f in found.custom_field_definitions)

    async def test_add_custom_field_not_found(self, handler) -> None:
        cmd = AddProjectCustomFieldCommand(
            caller_id=str(Id.generate()),
            project_id=str(Id.generate()),
            name="X",
            field_type="text",
        )
        with pytest.raises(ProjectNotFoundException):
            await handler.handle(cmd)
