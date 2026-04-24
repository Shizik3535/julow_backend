"""Unit-тесты для InterfaceDensity."""

import pytest

from app.context.profile.domain.value_objects.interface_density import InterfaceDensity


@pytest.mark.unit
class TestInterfaceDensity:
    def test_all_densities_exist(self) -> None:
        assert InterfaceDensity.COMPACT.value == "compact"
        assert InterfaceDensity.COMFORTABLE.value == "comfortable"
        assert InterfaceDensity.SPACIOUS.value == "spacious"

    def test_densities_are_distinct(self) -> None:
        values = [d.value for d in InterfaceDensity]
        assert len(values) == len(set(values))
