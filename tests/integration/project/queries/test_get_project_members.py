"""Интеграционные тесты GetProjectMembersHandler (реальные repos)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.project.application.queries.get_project_members import (
    GetProjectMembersQuery,
    GetProjectMembersHandler,
)


@pytest.mark.integration
class TestGetProjectMembersHandler:
    """Тесты GetProjectMembersHandler."""

    @pytest.fixture
    def handler(self, membership_repo) -> GetProjectMembersHandler:
        return GetProjectMembersHandler(membership_repo=membership_repo)

    async def test_get_members_with_members(self, handler, make_project_with_membership) -> None:
        data = await make_project_with_membership()
        query = GetProjectMembersQuery(project_id=str(data["project"].id))
        result = await handler.handle(query)
        assert len(result.items) >= 1

    async def test_get_members_empty(self, handler, make_project) -> None:
        project = await make_project()
        query = GetProjectMembersQuery(project_id=str(project.id))
        result = await handler.handle(query)
        assert len(result.items) == 0
