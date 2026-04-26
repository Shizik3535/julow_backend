"""Интеграционные тесты GetProjectsByMemberHandler (реальные repos)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.project.application.queries.get_projects_by_member import (
    GetProjectsByMemberQuery,
    GetProjectsByMemberHandler,
)


@pytest.mark.integration
class TestGetProjectsByMemberHandler:
    """Тесты GetProjectsByMemberHandler."""

    @pytest.fixture
    def handler(self, project_repo, permission_checker_stub) -> GetProjectsByMemberHandler:
        return GetProjectsByMemberHandler(project_repo=project_repo, permission_checker=permission_checker_stub)

    async def test_get_projects_by_member_found(self, handler, make_project_with_membership) -> None:
        data = await make_project_with_membership()
        query = GetProjectsByMemberQuery(caller_id=str(data["owner_id"]), user_id=str(data["owner_id"]))
        result = await handler.handle(query)
        assert len(result.items) >= 1

    async def test_get_projects_by_member_empty(self, handler) -> None:
        query = GetProjectsByMemberQuery(caller_id=str(Id.generate()), user_id=str(Id.generate()))
        result = await handler.handle(query)
        assert len(result.items) == 0
