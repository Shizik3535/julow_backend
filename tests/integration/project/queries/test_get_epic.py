"""Интеграционные тесты GetEpicHandler (реальные repos)."""

import pytest

from app.context.project.domain.exceptions.epic_exceptions import EpicNotFoundException
from app.shared.domain.value_objects.id_vo import Id
from app.context.project.application.queries.get_epic import (
    GetEpicQuery,
    GetEpicHandler,
)


@pytest.mark.integration
class TestGetEpicHandler:
    """Тесты GetEpicHandler."""

    @pytest.fixture
    def handler(self, epic_repo, permission_checker_stub) -> GetEpicHandler:
        return GetEpicHandler(epic_repo=epic_repo, permission_checker=permission_checker_stub)

    async def test_get_epic_found(self, handler, make_epic) -> None:
        epic = await make_epic(name="Feature Epic")
        query = GetEpicQuery(caller_id=str(Id.generate()), epic_id=str(epic.id))
        result = await handler.handle(query)
        assert result.name == "Feature Epic"

    async def test_get_epic_not_found(self, handler) -> None:
        query = GetEpicQuery(caller_id=str(Id.generate()), epic_id=str(Id.generate()))
        with pytest.raises(EpicNotFoundException):
            await handler.handle(query)
