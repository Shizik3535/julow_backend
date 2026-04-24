"""Unit-тесты для агрегата RetroTemplate (Project BC)."""

import pytest

from app.context.project.domain.aggregates.retro_template import RetroTemplate
from app.context.project.domain.value_objects.retro_section import RetroSection
from app.context.project.domain.events.retro_template_events import (
    RetroTemplateCreated,
    RetroTemplateUpdated,
    RetroTemplateDeleted,
)
from app.context.project.domain.exceptions.project_role_exceptions import (
    CannotDeleteSystemRoleException,
)


# ═══════════════════════════════════════════════════════════════════════════
# Создание
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestRetroTemplateCreation:
    def test_create_system(self) -> None:
        sections = [RetroSection(title="What went well")]
        template = RetroTemplate.create_system(name="Classic", sections=sections)
        assert template.name == "Classic"
        assert template.is_system
        assert template.sections == sections

    def test_create_system_emits_event(self) -> None:
        template = RetroTemplate.create_system(name="Classic", sections=[])
        events = template.clear_domain_events()
        assert len(events) == 1
        assert isinstance(events[0], RetroTemplateCreated)

    def test_create_custom(self, new_retro_template: RetroTemplate) -> None:
        assert new_retro_template.name == "Custom Retro"
        assert not new_retro_template.is_system
        assert len(new_retro_template.sections) == 2

    def test_create_custom_emits_event(self, new_retro_template: RetroTemplate) -> None:
        events = new_retro_template.clear_domain_events()
        assert len(events) == 1
        assert isinstance(events[0], RetroTemplateCreated)


# ═══════════════════════════════════════════════════════════════════════════
# Обновление
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestRetroTemplateUpdate:
    def test_update_sections(self, retro_template: RetroTemplate) -> None:
        new_sections = [RetroSection(title="New section")]
        retro_template.update(sections=new_sections)
        assert retro_template.sections == new_sections

    def test_update_emits_event(self, retro_template: RetroTemplate) -> None:
        retro_template.update(sections=[RetroSection(title="Updated")])
        events = retro_template.clear_domain_events()
        assert any(isinstance(e, RetroTemplateUpdated) for e in events)


# ═══════════════════════════════════════════════════════════════════════════
# Удаление
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestRetroTemplateDeletion:
    def test_assert_deletable_system_raises(self) -> None:
        template = RetroTemplate.create_system(name="Classic", sections=[])
        with pytest.raises(CannotDeleteSystemRoleException):
            template.assert_deletable()

    def test_mark_deleted_custom(self, retro_template: RetroTemplate) -> None:
        retro_template.mark_deleted()
        events = retro_template.clear_domain_events()
        assert any(isinstance(e, RetroTemplateDeleted) for e in events)

    def test_mark_deleted_system_raises(self) -> None:
        template = RetroTemplate.create_system(name="Classic", sections=[])
        with pytest.raises(CannotDeleteSystemRoleException):
            template.mark_deleted()
