"""Интеграционные тесты RemoveTaskAttachmentHandler (реальные repos + стабы портов)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.task.application.commands.remove_task_attachment import RemoveTaskAttachmentCommand, RemoveTaskAttachmentHandler
from app.context.task.application.exceptions.authorization_exceptions import InsufficientTaskPermissionsException
from app.context.task.domain.exceptions.task_exceptions import TaskNotFoundException


@pytest.mark.integration
class TestRemoveTaskAttachmentHandler:
    """Тесты удаления вложения — full stack."""

    @pytest.fixture
    def handler(self, task_repo, permission_checker_stub, event_bus_stub) -> RemoveTaskAttachmentHandler:
        return RemoveTaskAttachmentHandler(task_repo=task_repo, permission_checker=permission_checker_stub, event_bus=event_bus_stub)

    async def test_remove_attachment_success(self, handler, task_repo, make_task) -> None:
        task = await make_task()
        file_id = Id.generate()
        uploaded_by = Id.generate()
        task.add_attachment(file_id=file_id, filename="doc.pdf", size_bytes=100, uploaded_by=uploaded_by)
        task.clear_domain_events()
        await task_repo.update(task)

        cmd = RemoveTaskAttachmentCommand(
            caller_id=str(Id.generate()),
            task_id=str(task.id),
            file_id=str(task.attachments[0].file_id),
        )
        await handler.handle(cmd)

        found = await task_repo.get_by_id(task.id)
        assert found is not None
        assert len(found.attachments) == 0

    async def test_remove_attachment_task_not_found(self, handler) -> None:
        cmd = RemoveTaskAttachmentCommand(
            caller_id=str(Id.generate()),
            task_id=str(Id.generate()),
            file_id=str(Id.generate()),
        )
        with pytest.raises(TaskNotFoundException):
            await handler.handle(cmd)

    async def test_remove_attachment_permission_denied(self, task_repo, permission_denied_stub, event_bus_stub, make_task) -> None:
        task = await make_task()
        handler = RemoveTaskAttachmentHandler(task_repo=task_repo, permission_checker=permission_denied_stub, event_bus=event_bus_stub)
        cmd = RemoveTaskAttachmentCommand(
            caller_id=str(Id.generate()),
            task_id=str(task.id),
            file_id=str(Id.generate()),
        )
        with pytest.raises(InsufficientTaskPermissionsException):
            await handler.handle(cmd)
