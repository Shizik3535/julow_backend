"""Интеграционные тесты AddTaskAttachmentHandler (реальные repos + стабы портов)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.task.application.commands.add_task_attachment import AddTaskAttachmentCommand, AddTaskAttachmentHandler
from app.context.task.application.exceptions.authorization_exceptions import InsufficientTaskPermissionsException
from app.context.task.domain.exceptions.task_exceptions import TaskNotFoundException


@pytest.mark.integration
class TestAddTaskAttachmentHandler:
    """Тесты добавления вложения — full stack."""

    @pytest.fixture
    def handler(self, task_repo, file_storage_stub, permission_checker_stub, event_bus_stub) -> AddTaskAttachmentHandler:
        return AddTaskAttachmentHandler(
            task_repo=task_repo,
            file_storage=file_storage_stub,
            permission_checker=permission_checker_stub,
            event_bus=event_bus_stub,
        )

    async def test_add_attachment_success(self, handler, task_repo, make_task) -> None:
        task = await make_task()
        uploaded_by = Id.generate()

        cmd = AddTaskAttachmentCommand(
            caller_id=str(Id.generate()),
            task_id=str(task.id),
            filename="doc.pdf",
            file_data=b"PDF content here",
            content_type="application/pdf",
            uploaded_by=str(uploaded_by),
        )
        file_id = await handler.handle(cmd)

        found = await task_repo.get_by_id(task.id)
        assert found is not None
        assert len(found.attachments) == 1
        assert found.attachments[0].filename == "doc.pdf"
        assert found.attachments[0].size_bytes == 16

    async def test_add_attachment_task_not_found(self, handler) -> None:
        cmd = AddTaskAttachmentCommand(
            caller_id=str(Id.generate()),
            task_id=str(Id.generate()),
            filename="doc.pdf",
            file_data=b"data",
            uploaded_by=str(Id.generate()),
        )
        with pytest.raises(TaskNotFoundException):
            await handler.handle(cmd)

    async def test_add_attachment_permission_denied(self, task_repo, file_storage_stub, permission_denied_stub, event_bus_stub, make_task) -> None:
        task = await make_task()
        handler = AddTaskAttachmentHandler(
            task_repo=task_repo,
            file_storage=file_storage_stub,
            permission_checker=permission_denied_stub,
            event_bus=event_bus_stub,
        )
        cmd = AddTaskAttachmentCommand(
            caller_id=str(Id.generate()),
            task_id=str(task.id),
            filename="doc.pdf",
            file_data=b"data",
            content_type="application/pdf",
            uploaded_by=str(Id.generate()),
        )
        with pytest.raises(InsufficientTaskPermissionsException):
            await handler.handle(cmd)
