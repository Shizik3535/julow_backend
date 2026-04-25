"""Интеграционные тесты GetTaskTemplatesHandler (реальные repos + стабы портов)."""

import pytest

from app.context.task.application.queries.get_task_templates import GetTaskTemplatesQuery, GetTaskTemplatesHandler


@pytest.mark.integration
class TestGetTaskTemplatesHandler:
    """Тесты получения системных шаблонов — full stack."""

    @pytest.fixture
    def handler(self, task_template_repo) -> GetTaskTemplatesHandler:
        return GetTaskTemplatesHandler(template_repo=task_template_repo)

    async def test_get_system_templates(self, handler, make_task_template) -> None:
        await make_task_template(name="Sys1", is_system=True)
        result = await handler.handle(GetTaskTemplatesQuery())
        assert len(result.items) >= 1
