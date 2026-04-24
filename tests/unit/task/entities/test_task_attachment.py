"""Unit-тесты для TaskAttachment (Task BC)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.task.domain.entities.task_attachment import TaskAttachment


@pytest.mark.unit
class TestTaskAttachment:
    def test_create(self) -> None:
        file_id = Id.generate()
        uploaded_by = Id.generate()
        attachment = TaskAttachment(
            file_id=file_id,
            filename="doc.pdf",
            size_bytes=1024,
            uploaded_by=uploaded_by,
        )
        assert attachment.file_id == file_id
        assert attachment.filename == "doc.pdf"
        assert attachment.size_bytes == 1024
        assert attachment.uploaded_by == uploaded_by
        assert attachment.uploaded_at is not None
        assert attachment.id is not None

    def test_equality_by_id(self) -> None:
        shared_id = Id.generate()
        file_id = Id.generate()
        uploaded_by = Id.generate()
        a1 = TaskAttachment(id=shared_id, file_id=file_id, filename="a.pdf", size_bytes=1, uploaded_by=uploaded_by)
        a2 = TaskAttachment(id=shared_id, file_id=file_id, filename="a.pdf", size_bytes=1, uploaded_by=uploaded_by)
        assert a1 == a2

    def test_inequality_different_id(self) -> None:
        a1 = TaskAttachment(file_id=Id.generate(), filename="a.pdf", size_bytes=1, uploaded_by=Id.generate())
        a2 = TaskAttachment(file_id=Id.generate(), filename="a.pdf", size_bytes=1, uploaded_by=Id.generate())
        assert a1 != a2
