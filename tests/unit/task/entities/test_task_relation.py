"""Unit-тесты для TaskRelation (Task BC)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.task.domain.entities.task_relation import TaskRelation
from app.context.task.domain.value_objects.relation_type import RelationType


@pytest.mark.unit
class TestTaskRelation:
    def test_create(self) -> None:
        related_id = Id.generate()
        created_by = Id.generate()
        relation = TaskRelation(
            related_task_id=related_id,
            relation_type=RelationType.BLOCKS,
            created_by=created_by,
        )
        assert relation.related_task_id == related_id
        assert relation.relation_type == RelationType.BLOCKS
        assert relation.created_by == created_by
        assert relation.created_at is not None
        assert relation.id is not None

    def test_equality_by_id(self) -> None:
        shared_id = Id.generate()
        related_id = Id.generate()
        created_by = Id.generate()
        r1 = TaskRelation(id=shared_id, related_task_id=related_id, relation_type=RelationType.BLOCKS, created_by=created_by)
        r2 = TaskRelation(id=shared_id, related_task_id=related_id, relation_type=RelationType.BLOCKS, created_by=created_by)
        assert r1 == r2

    def test_inequality_different_id(self) -> None:
        r1 = TaskRelation(related_task_id=Id.generate(), relation_type=RelationType.BLOCKS, created_by=Id.generate())
        r2 = TaskRelation(related_task_id=Id.generate(), relation_type=RelationType.BLOCKS, created_by=Id.generate())
        assert r1 != r2
