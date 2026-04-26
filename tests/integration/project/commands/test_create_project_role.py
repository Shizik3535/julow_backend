"""Интеграционные тесты CreateProjectRoleHandler (реальные repos + реальные порты)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.project.application.commands.create_project_role import (
    CreateProjectRoleCommand,
    CreateProjectRoleHandler,
)
from app.context.project.application.exceptions.authorization_exceptions import (
    InsufficientProjectPermissionsException,
)
from tests.integration.project.conftest import (
    _AlwaysAllowProjectPermissionChecker,
    _NoopEventBus,
)


@pytest.mark.integration
class TestCreateProjectRoleHandler:
    """Тесты CreateProjectRoleHandler."""

    @pytest.fixture
    def handler(self, role_repo, project_repo, permission_checker_stub, event_bus_stub) -> CreateProjectRoleHandler:
        return CreateProjectRoleHandler(
            project_repo=project_repo,
            role_repo=role_repo,
            permission_checker=permission_checker_stub,
            event_bus=event_bus_stub,
        )

    async def test_create_role_success(self, handler, role_repo, make_project) -> None:
        project = await make_project()
        cmd = CreateProjectRoleCommand(
            caller_id=str(Id.generate()),
            project_id=str(project.id),
            name="Reviewer",
            permissions=["tasks.read", "members.read"],
        )
        result = await handler.handle(cmd)

        assert result.name == "Reviewer"
        assert "tasks.read" in result.permissions

        role = await role_repo.get_by_id(Id.from_string(result.id))
        assert role is not None

    async def test_create_role_insufficient_permission(self, role_repo, project_repo, event_bus_stub, make_project) -> None:
        from tests.integration.project.conftest import _AlwaysAllowProjectPermissionChecker

        project = await make_project()

        class _DenyChecker(_AlwaysAllowProjectPermissionChecker):
            async def has_permission(self, user_id, project_id, permission) -> bool:
                return False

            async def require_permission(self, user_id, project_id, permission) -> None:
                raise InsufficientProjectPermissionsException(
                    permission=permission, project_id=str(project_id),
                )

        handler = CreateProjectRoleHandler(
            project_repo=project_repo,
            role_repo=role_repo,
            permission_checker=_DenyChecker(),
            event_bus=event_bus_stub,
        )
        cmd = CreateProjectRoleCommand(
            caller_id=str(Id.generate()),
            project_id=str(project.id),
            name="X",
            permissions=[],
        )
        with pytest.raises(InsufficientProjectPermissionsException):
            await handler.handle(cmd)
