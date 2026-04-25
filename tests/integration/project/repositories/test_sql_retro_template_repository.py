"""Интеграционные тесты SqlRetroTemplateRepository (реальная PostgreSQL)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.project.domain.value_objects.retro_section import RetroSection
from app.context.project.domain.value_objects.retro_item_type import RetroItemType
from app.context.project.infrastructure.persistence.repositories.sql_retro_template_repository import (
    SqlRetroTemplateRepository,
)


@pytest.mark.integration
class TestSqlRetroTemplateRepositoryAdd:
    """Тесты добавления."""

    async def test_add_and_get_by_id(self, retro_template_repo: SqlRetroTemplateRepository, make_retro_template) -> None:
        template = await make_retro_template()
        found = await retro_template_repo.get_by_id(template.id)
        assert found is not None
        assert found.id == template.id

    async def test_add_persists_attributes(self, retro_template_repo: SqlRetroTemplateRepository, make_retro_template) -> None:
        template = await make_retro_template(name="My Retro")
        found = await retro_template_repo.get_by_id(template.id)
        assert found is not None
        assert found.name == "My Retro"
        assert found.is_system is False
        assert len(found.sections) == 2


@pytest.mark.integration
class TestSqlRetroTemplateRepositorySearch:
    """Тесты поиска."""

    async def test_get_system_templates(self, retro_template_repo: SqlRetroTemplateRepository, make_retro_template) -> None:
        await make_retro_template(name="SystemRetro", is_system=True)
        templates = await retro_template_repo.get_system_templates()
        assert len(templates) > 0
        assert all(t.is_system for t in templates)

    async def test_get_by_name(self, retro_template_repo: SqlRetroTemplateRepository, make_retro_template) -> None:
        template = await make_retro_template(name="UniqueRetroTemplate")
        found = await retro_template_repo.get_by_name("UniqueRetroTemplate")
        assert found is not None
        assert found.id == template.id

    async def test_get_by_name_not_found(self, retro_template_repo: SqlRetroTemplateRepository) -> None:
        found = await retro_template_repo.get_by_name("nonexistent-template")
        assert found is None


@pytest.mark.integration
class TestSqlRetroTemplateRepositoryUpdate:
    """Тесты обновления."""

    async def test_update_sections(self, retro_template_repo: SqlRetroTemplateRepository, make_retro_template) -> None:
        template = await make_retro_template()
        new_sections = [
            RetroSection(title="Start", item_type=RetroItemType.POSITIVE),
            RetroSection(title="Stop", item_type=RetroItemType.NEGATIVE),
            RetroSection(title="Continue", item_type=RetroItemType.NEUTRAL),
        ]
        template.update(sections=new_sections)
        template.clear_domain_events()
        await retro_template_repo.update(template)

        found = await retro_template_repo.get_by_id(template.id)
        assert found is not None
        assert len(found.sections) == 3


@pytest.mark.integration
class TestSqlRetroTemplateRepositoryDelete:
    """Тесты удаления."""

    async def test_delete(self, retro_template_repo: SqlRetroTemplateRepository, make_retro_template) -> None:
        template = await make_retro_template()
        await retro_template_repo.delete(template.id)
        found = await retro_template_repo.get_by_id(template.id)
        assert found is None

    async def test_get_by_id_not_found(self, retro_template_repo: SqlRetroTemplateRepository) -> None:
        found = await retro_template_repo.get_by_id(Id.generate())
        assert found is None
