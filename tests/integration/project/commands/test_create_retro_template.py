"""Интеграционные тесты CreateRetroTemplateHandler (реальные repos + реальные порты)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.project.application.commands.create_retro_template import (
    CreateRetroTemplateCommand,
    CreateRetroTemplateHandler,
)
from tests.integration.project.conftest import (
    _AlwaysAllowWorkspacePermissionChecker,
    _NoopEventBus,
)


@pytest.mark.integration
class TestCreateRetroTemplateHandler:
    """Тесты CreateRetroTemplateHandler."""

    @pytest.fixture
    def handler(self, retro_template_repo, workspace_permission_checker_stub, event_bus_stub) -> CreateRetroTemplateHandler:
        return CreateRetroTemplateHandler(
            retro_template_repo=retro_template_repo,
            workspace_permission_checker=workspace_permission_checker_stub,
            event_bus=event_bus_stub,
        )

    async def test_create_retro_template_success(self, handler, retro_template_repo) -> None:
        cmd = CreateRetroTemplateCommand(
            caller_id=str(Id.generate()),
            workspace_id=str(Id.generate()),
            name="My Retro",
            sections=[
                {"title": "What went well", "item_type": "positive"},
                {"title": "What to improve", "item_type": "negative"},
            ],
        )
        result = await handler.handle(cmd)

        assert result.name == "My Retro"
        assert result.is_system is False
        assert len(result.sections) == 2

        template = await retro_template_repo.get_by_id(Id.from_string(result.id))
        assert template is not None
