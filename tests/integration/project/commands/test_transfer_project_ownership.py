"""Интеграционные тесты TransferProjectOwnershipHandler (реальные repos + реальные порты)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.project.application.commands.transfer_project_ownership import (
    TransferProjectOwnershipCommand,
    TransferProjectOwnershipHandler,
)
from app.context.project.domain.exceptions.project_exceptions import ProjectNotFoundException
from tests.integration.project.conftest import (
    _AlwaysAllowProjectPermissionChecker,
    _NoopEventBus,
)


@pytest.mark.integration
class TestTransferProjectOwnershipHandler:
    """Тесты TransferProjectOwnershipHandler."""

    @pytest.fixture
    def handler(self, project_repo, permission_checker_stub, event_bus_stub) -> TransferProjectOwnershipHandler:
        return TransferProjectOwnershipHandler(
            project_repo=project_repo,
            permission_checker=permission_checker_stub,
            event_bus=event_bus_stub,
        )

    async def test_transfer_ownership_success(self, handler, project_repo, make_project, make_user) -> None:
        owner = await make_user()
        new_owner = await make_user()
        project = await make_project(owner_id=owner.id)

        cmd = TransferProjectOwnershipCommand(
            caller_id=str(owner.id),
            project_id=str(project.id),
            from_owner_id=str(owner.id),
            to_owner_id=str(new_owner.id),
        )
        await handler.handle(cmd)

        found = await project_repo.get_by_id(project.id)
        assert found is not None
        assert new_owner.id in found.owner_ids

    async def test_transfer_ownership_not_found(self, handler) -> None:
        cmd = TransferProjectOwnershipCommand(
            caller_id=str(Id.generate()),
            project_id=str(Id.generate()),
            from_owner_id=str(Id.generate()),
            to_owner_id=str(Id.generate()),
        )
        with pytest.raises(ProjectNotFoundException):
            await handler.handle(cmd)
