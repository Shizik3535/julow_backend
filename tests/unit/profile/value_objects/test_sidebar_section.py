"""Unit-тесты для SidebarSection."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.shared.domain.exceptions import ValidationException
from app.context.profile.domain.value_objects.sidebar_section import SidebarSection


@pytest.mark.unit
class TestSidebarSection:
    def test_create_section(self) -> None:
        section = SidebarSection(section_id="projects", is_collapsed=False, order=0)
        assert section.section_id == "projects"
        assert not section.is_collapsed
        assert section.order == 0

    def test_with_item_ids(self) -> None:
        ids = [Id.generate(), Id.generate()]
        section = SidebarSection(section_id="nav", item_ids=ids, order=1)
        assert len(section.item_ids) == 2

    def test_defaults(self) -> None:
        section = SidebarSection(section_id="default")
        assert section.is_collapsed is False
        assert section.item_ids == []
        assert section.order == 0

    def test_frozen(self) -> None:
        section = SidebarSection(section_id="nav")
        with pytest.raises(Exception):
            section.section_id = "changed"

    def test_equality_by_value(self) -> None:
        s1 = SidebarSection(section_id="nav", order=0)
        s2 = SidebarSection(section_id="nav", order=0)
        assert s1 == s2

    def test_empty_section_id_raises(self) -> None:
        with pytest.raises(ValidationException):
            SidebarSection(section_id="")

    def test_blank_section_id_raises(self) -> None:
        with pytest.raises(ValidationException):
            SidebarSection(section_id="   ")
