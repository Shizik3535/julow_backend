"""Интеграционные тесты GetProjectMemberHandler (реальные repos)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.project.application.queries.get_project_member import (
    GetProjectMemberQuery,
    GetProjectMemberHandler,
)


@pytest.mark.integration
class TestGetProjectMemberHandler:
    """Тесты GetProjectMemberHandler."""

    @pytest.fixture
    def handler(self, membership_repo) -> GetProjectMemberHandler:
        return GetProjectMemberHandler(membership_repo=membership_repo)

    async def test_get_member_found(self, handler, make_project_with_membership) -> None:
        data = await make_project_with_membership()
        owner_id = data["owner_id"]

        query = GetProjectMemberQuery(
            project_id=str(data["project"].id),
            user_id=str(owner_id),
        )
        result = await handler.handle(query)
        assert result is not None

    async def test_get_member_not_found(self, handler, make_project_with_membership) -> None:
        data = await make_project_with_membership()
        query = GetProjectMemberQuery(
            project_id=str(data["project"].id),
            user_id=str(Id.generate()),
        )
        from app.context.project.application.exceptions.membership_app_exceptions import MemberNotInProjectException
        with pytest.raises(MemberNotInProjectException):
            await handler.handle(query)
