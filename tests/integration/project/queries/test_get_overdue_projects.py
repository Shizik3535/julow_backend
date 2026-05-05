"""Интеграционные тесты GetOverdueProjectsHandler (реальные repos)."""

from datetime import date, timedelta

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.project.application.queries.get_overdue_projects import (
    GetOverdueProjectsQuery,
    GetOverdueProjectsHandler,
)


@pytest.mark.integration
class TestGetOverdueProjectsHandler:
    """Тесты GetOverdueProjectsHandler."""

    @pytest.fixture
    def handler(self, project_repo, permission_checker_stub) -> GetOverdueProjectsHandler:
        return GetOverdueProjectsHandler(project_repo=project_repo, permission_checker=permission_checker_stub)

    async def test_my_overdue_projects_returns_member_projects(self, handler, make_project_with_membership) -> None:
        user_id = Id.generate()
        result_dict = await make_project_with_membership(owner_id=user_id)
        project = result_dict["project"]
        project.update_info(deadline=date.today() - timedelta(days=1))
        project.clear_domain_events()

        query = GetOverdueProjectsQuery(caller_id=str(user_id))
        result = await handler.handle(query)
        assert any(item.id == str(project.id) for item in result.items)

    async def test_my_overdue_projects_excludes_future_deadline(self, handler, make_project_with_membership) -> None:
        user_id = Id.generate()
        result_dict = await make_project_with_membership(owner_id=user_id)
        project = result_dict["project"]
        project.update_info(deadline=date.today() + timedelta(days=7))
        project.clear_domain_events()

        query = GetOverdueProjectsQuery(caller_id=str(user_id))
        result = await handler.handle(query)
        assert not any(item.id == str(project.id) for item in result.items)

    async def test_workspace_overdue_projects_filters_by_workspace(self, handler, make_project) -> None:
        ws_id = Id.generate()
        other_ws_id = Id.generate()
        project_in_ws = await make_project(workspace_id=ws_id)
        project_in_ws.update_info(deadline=date.today() - timedelta(days=1))
        project_in_ws.clear_domain_events()

        project_other_ws = await make_project(workspace_id=other_ws_id)
        project_other_ws.update_info(deadline=date.today() - timedelta(days=1))
        project_other_ws.clear_domain_events()

        query = GetOverdueProjectsQuery(caller_id=str(Id.generate()), workspace_id=str(ws_id))
        result = await handler.handle(query)
        assert any(item.id == str(project_in_ws.id) for item in result.items)
        assert not any(item.id == str(project_other_ws.id) for item in result.items)

    async def test_workspace_overdue_projects_empty(self, handler) -> None:
        query = GetOverdueProjectsQuery(caller_id=str(Id.generate()), workspace_id=str(Id.generate()))
        result = await handler.handle(query)
        assert len(result.items) == 0
