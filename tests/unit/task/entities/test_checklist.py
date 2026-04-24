"""Unit-тесты для Checklist (Task BC)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.task.domain.entities.checklist import Checklist


@pytest.mark.unit
class TestChecklist:
    def test_create(self) -> None:
        cl = Checklist(title="Steps")
        assert cl.title == "Steps"
        assert cl.items == []
        assert cl.id is not None

    def test_equality_by_id(self) -> None:
        shared_id = Id.generate()
        cl1 = Checklist(id=shared_id, title="A")
        cl2 = Checklist(id=shared_id, title="A")
        assert cl1 == cl2

    def test_inequality_different_id(self) -> None:
        cl1 = Checklist(title="A")
        cl2 = Checklist(title="A")
        assert cl1 != cl2
