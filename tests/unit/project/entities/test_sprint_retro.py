"""Unit-тесты для SprintRetro (Project BC)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.project.domain.entities.sprint_retro import SprintRetro
from app.context.project.domain.value_objects.retro_section import RetroSection


@pytest.mark.unit
class TestSprintRetro:
    def test_create(self) -> None:
        sections = [RetroSection(title="What went well")]
        retro = SprintRetro(template_name="Classic", sections=sections)
        assert retro.template_name == "Classic"
        assert retro.sections == sections
        assert retro.id is not None
        assert retro.items == []
        assert retro.created_at is not None

    def test_equality_by_id(self) -> None:
        shared_id = Id.generate()
        r1 = SprintRetro(id=shared_id, template_name="Classic")
        r2 = SprintRetro(id=shared_id, template_name="Classic")
        assert r1 == r2

    def test_inequality_different_id(self) -> None:
        r1 = SprintRetro(template_name="Classic")
        r2 = SprintRetro(template_name="Classic")
        assert r1 != r2
