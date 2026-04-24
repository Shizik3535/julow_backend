"""Unit-тесты для PinnedItem."""

from datetime import datetime, timezone

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.profile.domain.entities.pinned_item import PinnedItem
from app.context.profile.domain.value_objects.pinned_target_type import PinnedTargetType


@pytest.mark.unit
class TestPinnedItem:
    def test_create_pinned_item(self) -> None:
        tid = Id.generate()
        item = PinnedItem(target_type=PinnedTargetType.PROJECT, target_id=tid, order=0)
        assert item.target_type == PinnedTargetType.PROJECT
        assert item.target_id == tid
        assert item.order == 0
        assert isinstance(item.pinned_at, datetime)

    def test_default_target_type(self) -> None:
        item = PinnedItem()
        assert item.target_type == PinnedTargetType.TASK

    def test_equality_by_id(self) -> None:
        shared_id = Id.generate()
        tid = Id.generate()
        i1 = PinnedItem(id=shared_id, target_type=PinnedTargetType.TASK, target_id=tid)
        i2 = PinnedItem(id=shared_id, target_type=PinnedTargetType.TASK, target_id=tid)
        assert i1 == i2

    def test_inequality_different_id(self) -> None:
        tid = Id.generate()
        i1 = PinnedItem(target_type=PinnedTargetType.TASK, target_id=tid)
        i2 = PinnedItem(target_type=PinnedTargetType.TASK, target_id=tid)
        assert i1 != i2

    def test_pinned_at_is_utc(self) -> None:
        item = PinnedItem()
        assert item.pinned_at.tzinfo == timezone.utc
