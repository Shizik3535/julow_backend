"""Интеграционные тесты GetRetroTemplatesHandler (реальные repos)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.project.application.queries.get_retro_templates import (
    GetRetroTemplatesQuery,
    GetRetroTemplatesHandler,
)


@pytest.mark.integration
class TestGetRetroTemplatesHandler:
    """Тесты GetRetroTemplatesHandler."""

    @pytest.fixture
    def handler(self, retro_template_repo) -> GetRetroTemplatesHandler:
        return GetRetroTemplatesHandler(retro_template_repo=retro_template_repo)

    async def test_get_retro_templates_with_templates(self, handler, make_retro_template) -> None:
        await make_retro_template(name="SystemRetro", is_system=True)
        query = GetRetroTemplatesQuery()
        result = await handler.handle(query)
        assert len(result.items) >= 1
        assert all(t.is_system for t in result.items)

    async def test_get_retro_templates_custom_not_included(self, handler, make_retro_template) -> None:
        await make_retro_template(name="CustomRetro", is_system=False)
        query = GetRetroTemplatesQuery()
        result = await handler.handle(query)
        assert not any(t.name == "CustomRetro" for t in result.items)
