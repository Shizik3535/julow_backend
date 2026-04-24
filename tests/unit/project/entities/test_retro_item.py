"""Unit-тесты для RetroItem (Project BC)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.project.domain.entities.retro_item import RetroItem


@pytest.mark.unit
class TestRetroItem:
    def test_create(self) -> None:
        section_id = Id.generate()
        author_id = Id.generate()
        item = RetroItem(section_id=section_id, content="Need better testing", author_id=author_id)
        assert item.section_id == section_id
        assert item.content == "Need better testing"
        assert item.author_id == author_id
        assert item.id is not None
        assert item.votes == 0
        assert item.created_at is not None

    def test_equality_by_id(self) -> None:
        shared_id = Id.generate()
        section_id = Id.generate()
        author_id = Id.generate()
        i1 = RetroItem(id=shared_id, section_id=section_id, content="A", author_id=author_id)
        i2 = RetroItem(id=shared_id, section_id=section_id, content="A", author_id=author_id)
        assert i1 == i2

    def test_inequality_different_id(self) -> None:
        i1 = RetroItem(content="A")
        i2 = RetroItem(content="A")
        assert i1 != i2
