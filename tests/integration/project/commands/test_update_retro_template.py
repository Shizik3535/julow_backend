"""Интеграционные тесты UpdateRetroTemplateHandler (реальные repos + реальные порты)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.project.application.commands.update_retro_template import (
    UpdateRetroTemplateCommand,
    UpdateRetroTemplateHandler,
)
from tests.integration.project.conftest import (
    _AlwaysAllowWorkspacePermissionChecker,
    _NoopEventBus,
)


@pytest.mark.integration
class TestUpdateRetroTemplateHandler:
    """Тесты UpdateRetroTemplateHandler."""

    @pytest.fixture
    def handler(self, retro_template_repo, workspace_permission_checker_stub, event_bus_stub) -> UpdateRetroTemplateHandler:
        return UpdateRetroTemplateHandler(
            retro_template_repo=retro_template_repo,
            workspace_permission_checker=workspace_permission_checker_stub,
            event_bus=event_bus_stub,
        )

    async def test_update_retro_template_success(self, handler, retro_template_repo, make_retro_template) -> None:
        template = await make_retro_template(name="Old Template")
        new_sections = [
            {"title": "Start", "prompt": None, "item_type": "positive"},
            {"title": "Stop", "prompt": None, "item_type": "negative"},
            {"title": "Continue", "prompt": None, "item_type": "neutral"},
        ]
        cmd = UpdateRetroTemplateCommand(
            caller_id=str(Id.generate()),
            workspace_id=str(Id.generate()),
            template_id=str(template.id),
            sections=new_sections,
        )
        await handler.handle(cmd)

        found = await retro_template_repo.get_by_id(template.id)
        assert found is not None
        assert len(found.sections) == 3
