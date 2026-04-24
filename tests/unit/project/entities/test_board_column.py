"""Unit-тесты для BoardColumn (Project BC)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.project.domain.entities.board_column import BoardColumn
from app.context.project.domain.value_objects.wip_limit import WIPLimit


@pytest.mark.unit
class TestBoardColumn:
    def test_create(self) -> None:
        column = BoardColumn(name="To Do", order=0)
        assert column.name == "To Do"
        assert column.order == 0
        assert column.id is not None
        assert column.color is None
        assert column.wip_limit is None
        assert column.status_mapping is None

    def test_create_with_wip_limit(self) -> None:
        wip = WIPLimit(value=5)
        column = BoardColumn(name="In Progress", order=1, wip_limit=wip)
        assert column.wip_limit == wip

    def test_equality_by_id(self) -> None:
        shared_id = Id.generate()
        c1 = BoardColumn(id=shared_id, name="To Do", order=0)
        c2 = BoardColumn(id=shared_id, name="To Do", order=0)
        assert c1 == c2

    def test_inequality_different_id(self) -> None:
        c1 = BoardColumn(name="To Do", order=0)
        c2 = BoardColumn(name="To Do", order=0)
        assert c1 != c2
