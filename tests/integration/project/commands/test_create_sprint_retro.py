"""Интеграционные тесты CreateSprintRetroHandler (реальные repos + реальные порты)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.project.application.commands.create_sprint_retro import (
    CreateSprintRetroCommand,
    CreateSprintRetroHandler,
)
from tests.integration.project.conftest import (
    _AlwaysAllowProjectPermissionChecker,
    _NoopEventBus,
)


@pytest.mark.integration
class TestCreateSprintRetroHandler:
    """Тесты CreateSprintRetroHandler."""

    @pytest.fixture
    def handler(self, sprint_repo, retro_template_repo, permission_checker_stub, event_bus_stub) -> CreateSprintRetroHandler:
        return CreateSprintRetroHandler(
            sprint_repo=sprint_repo,
            retro_template_repo=retro_template_repo,
            permission_checker=permission_checker_stub,
            event_bus=event_bus_stub,
        )

    async def test_create_sprint_retro_success(self, handler, sprint_repo, make_sprint, make_retro_template) -> None:
        sprint = await make_sprint()
        sprint.start()
        sprint.clear_domain_events()
        await sprint_repo.update(sprint)

        template = await make_retro_template(name="RetroTpl", is_system=True)

        cmd = CreateSprintRetroCommand(
            caller_id=str(Id.generate()),
            sprint_id=str(sprint.id),
            template_id=str(template.id),
        )
        await handler.handle(cmd)

        found = await sprint_repo.get_by_id(sprint.id)
        assert found is not None
