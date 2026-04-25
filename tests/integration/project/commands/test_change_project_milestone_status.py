"""Интеграционные тесты ChangeProjectMilestoneStatusHandler (реальные repos + реальные порты)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.project.application.commands.change_project_milestone_status import (
    ChangeProjectMilestoneStatusCommand,
    ChangeProjectMilestoneStatusHandler,
)
from app.context.project.domain.exceptions.project_exceptions import ProjectNotFoundException
from tests.integration.project.conftest import (
    _AlwaysAllowProjectPermissionChecker,
    _NoopEventBus,
)


@pytest.mark.integration
class TestChangeProjectMilestoneStatusHandler:
    """Тесты ChangeProjectMilestoneStatusHandler."""

    @pytest.fixture
    def handler(self, project_repo, permission_checker_stub, event_bus_stub) -> ChangeProjectMilestoneStatusHandler:
        return ChangeProjectMilestoneStatusHandler(
            project_repo=project_repo,
            permission_checker=permission_checker_stub,
            event_bus=event_bus_stub,
        )

    async def test_change_milestone_status_success(self, handler, project_repo, make_project) -> None:
        from app.context.project.domain.value_objects.methodology import Methodology
        from app.context.project.domain.entities.milestone import Milestone
        from datetime import date

        project = await make_project(methodology=Methodology.WATERFALL)
        milestone = Milestone(name="v1.0", due_date=date(2026, 12, 31))
        project.add_milestone(milestone)
        project.clear_domain_events()
        await project_repo.update(project)

        cmd = ChangeProjectMilestoneStatusCommand(
            caller_id=str(Id.generate()),
            project_id=str(project.id),
            milestone_id=str(milestone.id),
            new_status="completed",
        )
        await handler.handle(cmd)

        found = await project_repo.get_by_id(project.id)
        assert found is not None

    async def test_change_milestone_status_not_found(self, handler) -> None:
        cmd = ChangeProjectMilestoneStatusCommand(
            caller_id=str(Id.generate()),
            project_id=str(Id.generate()),
            milestone_id=str(Id.generate()),
            new_status="completed",
        )
        with pytest.raises(ProjectNotFoundException):
            await handler.handle(cmd)
