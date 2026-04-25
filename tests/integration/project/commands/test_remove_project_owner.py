"""Интеграционные тесты RemoveProjectOwnerHandler (реальные repos + реальные порты)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.project.application.commands.remove_project_owner import (
    RemoveProjectOwnerCommand,
    RemoveProjectOwnerHandler,
)
from app.context.project.domain.exceptions.project_exceptions import ProjectNotFoundException
from tests.integration.project.conftest import (
    _AlwaysAllowProjectPermissionChecker,
    _NoopEventBus,
)


@pytest.mark.integration
class TestRemoveProjectOwnerHandler:
    """Тесты RemoveProjectOwnerHandler."""

    @pytest.fixture
    def handler(self, project_repo, permission_checker_stub, event_bus_stub) -> RemoveProjectOwnerHandler:
        return RemoveProjectOwnerHandler(
            project_repo=project_repo,
            permission_checker=permission_checker_stub,
            event_bus=event_bus_stub,
        )

    async def test_remove_owner_success(self, handler, project_repo, make_project, make_user) -> None:
        owner = await make_user()
        co_owner = await make_user()
        project = await make_project(owner_id=owner.id)

        project.add_owner(co_owner.id)
        project.clear_domain_events()
        await project_repo.update(project)

        cmd = RemoveProjectOwnerCommand(
            caller_id=str(owner.id),
            project_id=str(project.id),
            user_id=str(co_owner.id),
        )
        await handler.handle(cmd)

        found = await project_repo.get_by_id(project.id)
        assert found is not None
        assert co_owner.id not in found.owner_ids

    async def test_remove_owner_not_found(self, handler) -> None:
        cmd = RemoveProjectOwnerCommand(
            caller_id=str(Id.generate()),
            project_id=str(Id.generate()),
            user_id=str(Id.generate()),
        )
        with pytest.raises(ProjectNotFoundException):
            await handler.handle(cmd)
