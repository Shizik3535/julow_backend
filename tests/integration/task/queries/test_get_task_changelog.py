"""Интеграционные тесты GetTaskChangelogHandler (реальные repos + стабы портов)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.task.application.queries.get_task_changelog import GetTaskChangelogQuery, GetTaskChangelogHandler
from app.context.task.application.exceptions.authorization_exceptions import InsufficientTaskPermissionsException


@pytest.mark.integration
class TestGetTaskChangelogHandler:
    """Тесты получения истории изменений — full stack."""

    @pytest.fixture
    def handler(self, changelog_repo, task_repo, permission_checker_stub) -> GetTaskChangelogHandler:
        return GetTaskChangelogHandler(changelog_repo=changelog_repo, task_repo=task_repo, permission_checker=permission_checker_stub)

    async def test_get_changelog_found(self, handler, make_changelog_entry) -> None:
        entry = await make_changelog_entry(field_name="status_id")
        result = await handler.handle(GetTaskChangelogQuery(caller_id=str(Id.generate()), task_id=str(entry.task_id)))
        assert result.total >= 1

    async def test_get_changelog_empty(self, handler, make_task) -> None:
        task = await make_task()
        result = await handler.handle(GetTaskChangelogQuery(caller_id=str(Id.generate()), task_id=str(task.id)))
        assert result.total == 0

    async def test_get_changelog_pagination(self, handler, make_changelog_entry, make_task) -> None:
        task = await make_task()
        for i in range(5):
            await make_changelog_entry(task_id=task.id, field_name=f"field_{i}")
        result = await handler.handle(GetTaskChangelogQuery(caller_id=str(Id.generate()), task_id=str(task.id), offset=0, limit=2))
        assert len(result.items) <= 2

    async def test_get_changelog_permission_denied(self, changelog_repo, task_repo, permission_denied_stub, make_changelog_entry) -> None:
        entry = await make_changelog_entry(field_name="status_id")
        handler = GetTaskChangelogHandler(changelog_repo=changelog_repo, task_repo=task_repo, permission_checker=permission_denied_stub)
        with pytest.raises(InsufficientTaskPermissionsException):
            await handler.handle(GetTaskChangelogQuery(caller_id=str(Id.generate()), task_id=str(entry.task_id)))
