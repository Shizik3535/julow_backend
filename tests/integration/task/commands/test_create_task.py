"""Интеграционные тесты CreateTaskHandler (реальные repos + стабы портов)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.task.application.commands.create_task import CreateTaskCommand, CreateTaskHandler
from app.context.task.application.exceptions.authorization_exceptions import InsufficientTaskPermissionsException
from app.context.task.application.exceptions.task_app_exceptions import (
    TaskProjectNotFoundException,
    TaskProjectArchivedOrSuspendedException,
)
from app.context.task.domain.value_objects.task_status import TaskStatus


@pytest.mark.integration
class TestCreateTaskHandler:
    """Тесты создания задачи — full stack."""

    @pytest.fixture
    def handler(self, task_repo, project_stub, board_stub, permission_checker_stub, event_bus_stub) -> CreateTaskHandler:
        return CreateTaskHandler(
            task_repo=task_repo,
            project_port=project_stub,
            board_port=board_stub,
            permission_checker=permission_checker_stub,
            event_bus=event_bus_stub,
        )

    async def test_create_task_success(self, handler, task_repo, make_project) -> None:
        project = await make_project()
        reporter_id = Id.generate()

        cmd = CreateTaskCommand(
            caller_id=str(reporter_id),
            project_id=str(project.id),
            title="New Task",
            task_type="task",
            reporter_id=str(reporter_id),
        )
        result = await handler.handle(cmd)
        assert result is not None
        assert result.title == "New Task"

        found = await task_repo.get_by_id(Id.from_string(result.id))
        assert found is not None
        assert found.title == "New Task"
        assert found.project_id == project.id
        assert found.status == TaskStatus.ACTIVE

    async def test_create_task_with_epic(self, handler, task_repo, make_project) -> None:
        project = await make_project()
        epic_id = Id.generate()
        reporter_id = Id.generate()

        cmd = CreateTaskCommand(
            caller_id=str(reporter_id),
            project_id=str(project.id),
            title="Task with Epic",
            task_type="task",
            reporter_id=str(reporter_id),
            epic_id=str(epic_id),
        )
        result = await handler.handle(cmd)
        found = await task_repo.get_by_id(Id.from_string(result.id))
        assert found is not None
        assert found.epic_id == epic_id

    async def test_create_task_project_not_found(self, handler) -> None:
        class _NotFoundProjectPort(handler._project_port.__class__):
            async def project_exists(self, project_id: str) -> bool:
                return False

        handler._project_port = _NotFoundProjectPort()

        cmd = CreateTaskCommand(
            caller_id=str(Id.generate()),
            project_id=str(Id.generate()),
            title="Orphan Task",
        )
        with pytest.raises(TaskProjectNotFoundException):
            await handler.handle(cmd)

    async def test_create_task_project_archived(self, handler) -> None:
        class _ArchivedProjectPort(handler._project_port.__class__):
            async def project_exists(self, project_id: str) -> bool:
                return True

            async def is_project_active(self, project_id: str) -> bool:
                return False

        handler._project_port = _ArchivedProjectPort()

        cmd = CreateTaskCommand(
            caller_id=str(Id.generate()),
            project_id=str(Id.generate()),
            title="Archived Project Task",
        )
        with pytest.raises(TaskProjectArchivedOrSuspendedException):
            await handler.handle(cmd)

    async def test_create_task_permission_denied(self, task_repo, project_stub, board_stub, permission_denied_stub, event_bus_stub, make_project) -> None:
        project = await make_project()
        handler = CreateTaskHandler(
            task_repo=task_repo,
            project_port=project_stub,
            board_port=board_stub,
            permission_checker=permission_denied_stub,
            event_bus=event_bus_stub,
        )
        cmd = CreateTaskCommand(
            caller_id=str(Id.generate()),
            project_id=str(project.id),
            title="Denied Task",
        )
        with pytest.raises(InsufficientTaskPermissionsException):
            await handler.handle(cmd)
