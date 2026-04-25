"""Интеграционные тесты SqlBoardRepository (реальная PostgreSQL)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.shared.domain.value_objects.color_vo import Color
from app.context.project.domain.aggregates.board import Board
from app.context.project.domain.value_objects.methodology import Methodology
from app.context.project.domain.value_objects.wip_limit import WIPLimit
from app.context.project.infrastructure.persistence.repositories.sql_board_repository import SqlBoardRepository


@pytest.mark.integration
class TestSqlBoardRepositoryAdd:
    """Тесты добавления."""

    async def test_add_and_get_by_id(self, board_repo: SqlBoardRepository, make_project) -> None:
        proj = await make_project()
        board = Board.create(project_id=proj.id, methodology=Methodology.KANBAN)
        board.clear_domain_events()
        await board_repo.add(board)

        found = await board_repo.get_by_id(board.id)
        assert found is not None
        assert found.id == board.id

    async def test_add_and_get_by_project_id(self, board_repo: SqlBoardRepository, make_project) -> None:
        proj = await make_project()
        board = Board.create(project_id=proj.id, methodology=Methodology.KANBAN)
        board.clear_domain_events()
        await board_repo.add(board)

        found = await board_repo.get_by_project_id(proj.id)
        assert found is not None
        assert found.project_id == proj.id

    async def test_add_persists_default_columns(self, board_repo: SqlBoardRepository, make_project) -> None:
        proj = await make_project()
        board = Board.create(project_id=proj.id, methodology=Methodology.KANBAN)
        board.clear_domain_events()
        await board_repo.add(board)

        found = await board_repo.get_by_id(board.id)
        assert found is not None
        assert len(found.columns) > 0


@pytest.mark.integration
class TestSqlBoardRepositoryUpdate:
    """Тесты обновления дочерних коллекций."""

    async def test_update_add_column(self, board_repo: SqlBoardRepository, make_project) -> None:
        proj = await make_project()
        board = Board.create(project_id=proj.id, methodology=Methodology.KANBAN)
        board.clear_domain_events()
        await board_repo.add(board)

        board.add_column(name="New Column", color=Color("#FF0000"), wip_limit=WIPLimit(value=5))
        board.clear_domain_events()
        await board_repo.update(board)

        found = await board_repo.get_by_id(board.id)
        assert found is not None
        assert any(c.name == "New Column" for c in found.columns)

    async def test_update_add_swimlane(self, board_repo: SqlBoardRepository, make_project) -> None:
        proj = await make_project()
        board = Board.create(project_id=proj.id, methodology=Methodology.KANBAN)
        board.clear_domain_events()
        await board_repo.add(board)

        from app.context.project.domain.value_objects.swimlane_group_by import SwimlaneGroupBy
        board.add_swimlane(name="My Swimlane", group_by=SwimlaneGroupBy.ASSIGNEE)
        board.clear_domain_events()
        await board_repo.update(board)

        found = await board_repo.get_by_id(board.id)
        assert found is not None
        assert any(s.name == "My Swimlane" for s in found.swimlanes)


@pytest.mark.integration
class TestSqlBoardRepositoryDelete:
    """Тесты удаления."""

    async def test_delete(self, board_repo: SqlBoardRepository, make_project) -> None:
        proj = await make_project()
        board = Board.create(project_id=proj.id, methodology=Methodology.KANBAN)
        board.clear_domain_events()
        await board_repo.add(board)

        await board_repo.delete(board.id)
        found = await board_repo.get_by_id(board.id)
        assert found is None

    async def test_get_by_project_id_not_found(self, board_repo: SqlBoardRepository) -> None:
        found = await board_repo.get_by_project_id(Id.generate())
        assert found is None
