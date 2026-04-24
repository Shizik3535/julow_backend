"""Unit-тесты для ChecklistItem (Task BC)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.task.domain.entities.checklist_item import ChecklistItem


@pytest.mark.unit
class TestChecklistItem:
    def test_create(self) -> None:
        item = ChecklistItem(text="Do something")
        assert item.text == "Do something"
        assert item.is_checked is False
        assert item.order == 0
        assert item.assignee_id is None
        assert item.due_date is None
        assert item.checked_at is None
        assert item.id is not None

    def test_equality_by_id(self) -> None:
        shared_id = Id.generate()
        i1 = ChecklistItem(id=shared_id, text="A")
        i2 = ChecklistItem(id=shared_id, text="A")
        assert i1 == i2

    def test_inequality_different_id(self) -> None:
        i1 = ChecklistItem(text="A")
        i2 = ChecklistItem(text="A")
        assert i1 != i2
