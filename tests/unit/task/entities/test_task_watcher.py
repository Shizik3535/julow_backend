"""Unit-тесты для TaskWatcher (Task BC)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.task.domain.entities.task_watcher import TaskWatcher


@pytest.mark.unit
class TestTaskWatcher:
    def test_create(self) -> None:
        user_id = Id.generate()
        watcher = TaskWatcher(user_id=user_id)
        assert watcher.user_id == user_id
        assert watcher.watched_at is not None
        assert watcher.id is not None

    def test_equality_by_id(self) -> None:
        shared_id = Id.generate()
        user_id = Id.generate()
        w1 = TaskWatcher(id=shared_id, user_id=user_id)
        w2 = TaskWatcher(id=shared_id, user_id=user_id)
        assert w1 == w2

    def test_inequality_different_id(self) -> None:
        w1 = TaskWatcher(user_id=Id.generate())
        w2 = TaskWatcher(user_id=Id.generate())
        assert w1 != w2
