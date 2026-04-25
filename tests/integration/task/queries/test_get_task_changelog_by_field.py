"""Интеграционные тесты GetTaskChangelogByFieldHandler (реальные repos + стабы портов)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.task.application.queries.get_task_changelog_by_field import GetTaskChangelogByFieldQuery, GetTaskChangelogByFieldHandler
from app.context.task.application.exceptions.authorization_exceptions import InsufficientTaskPermissionsException


@pytest.mark.integration
class TestGetTaskChangelogByFieldHandler:
    """Тесты получения истории изменений по полю — full stack."""

    @pytest.fixture
    def handler(self, changelog_repo, task_repo, permission_checker_stub) -> GetTaskChangelogByFieldHandler:
        return GetTaskChangelogByFieldHandler(changelog_repo=changelog_repo, task_repo=task_repo, permission_checker=permission_checker_stub)

    async def test_get_changelog_by_field_found(self, handler, make_changelog_entry) -> None:
        entry = await make_changelog_entry(field_name="priority")
        result = await handler.handle(GetTaskChangelogByFieldQuery(caller_id=str(Id.generate()), task_id=str(entry.task_id), field_name="priority"))
        assert len(result.items) >= 1

    async def test_get_changelog_by_field_empty(self, handler, make_changelog_entry) -> None:
        entry = await make_changelog_entry(field_name="status_id")
        result = await handler.handle(GetTaskChangelogByFieldQuery(caller_id=str(Id.generate()), task_id=str(entry.task_id), field_name="priority"))
        assert len(result.items) == 0

    async def test_get_changelog_by_field_permission_denied(self, changelog_repo, task_repo, permission_denied_stub, make_changelog_entry) -> None:
        entry = await make_changelog_entry(field_name="priority")
        handler = GetTaskChangelogByFieldHandler(changelog_repo=changelog_repo, task_repo=task_repo, permission_checker=permission_denied_stub)
        with pytest.raises(InsufficientTaskPermissionsException):
            await handler.handle(GetTaskChangelogByFieldQuery(caller_id=str(Id.generate()), task_id=str(entry.task_id), field_name="priority"))
