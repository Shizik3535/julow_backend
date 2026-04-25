"""Интеграционные тесты DeleteRetroTemplateHandler (реальные repos + реальные порты)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.project.application.commands.delete_retro_template import (
    DeleteRetroTemplateCommand,
    DeleteRetroTemplateHandler,
)
from tests.integration.project.conftest import (
    _AlwaysAllowWorkspacePermissionChecker,
    _NoopEventBus,
)


@pytest.mark.integration
class TestDeleteRetroTemplateHandler:
    """Тесты DeleteRetroTemplateHandler."""

    @pytest.fixture
    def handler(self, retro_template_repo, workspace_permission_checker_stub, event_bus_stub) -> DeleteRetroTemplateHandler:
        return DeleteRetroTemplateHandler(
            retro_template_repo=retro_template_repo,
            workspace_permission_checker=workspace_permission_checker_stub,
            event_bus=event_bus_stub,
        )

    async def test_delete_retro_template_success(self, handler, retro_template_repo, make_retro_template) -> None:
        template = await make_retro_template()
        cmd = DeleteRetroTemplateCommand(
            caller_id=str(Id.generate()),
            workspace_id=str(Id.generate()),
            template_id=str(template.id),
        )
        await handler.handle(cmd)

        found = await retro_template_repo.get_by_id(template.id)
        assert found is None
