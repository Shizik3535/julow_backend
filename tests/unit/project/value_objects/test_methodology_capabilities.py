"""Unit-тесты для MethodologyCapabilities (Project BC)."""

import pytest

from app.context.project.domain.value_objects.methodology import Methodology
from app.context.project.domain.value_objects.methodology_capabilities import MethodologyCapabilities


@pytest.mark.unit
class TestMethodologyCapabilities:
    def test_defaults(self) -> None:
        caps = MethodologyCapabilities()
        assert not caps.has_sprints
        assert not caps.has_backlog
        assert not caps.has_milestones
        assert not caps.has_epics
        assert not caps.has_wip_limits
        assert not caps.has_velocity
        assert not caps.has_retros
        assert not caps.has_burndown

    def test_for_kanban(self) -> None:
        caps = MethodologyCapabilities.for_methodology(Methodology.KANBAN)
        assert not caps.has_sprints
        assert not caps.has_backlog
        assert caps.has_milestones
        assert caps.has_epics
        assert caps.has_wip_limits
        assert not caps.has_velocity
        assert not caps.has_retros
        assert not caps.has_burndown

    def test_for_scrum(self) -> None:
        caps = MethodologyCapabilities.for_methodology(Methodology.SCRUM)
        assert caps.has_sprints
        assert caps.has_backlog
        assert not caps.has_milestones
        assert caps.has_epics
        assert not caps.has_wip_limits
        assert caps.has_velocity
        assert caps.has_retros
        assert caps.has_burndown

    def test_for_waterfall(self) -> None:
        caps = MethodologyCapabilities.for_methodology(Methodology.WATERFALL)
        assert not caps.has_sprints
        assert not caps.has_backlog
        assert caps.has_milestones
        assert caps.has_epics
        assert not caps.has_wip_limits
        assert not caps.has_velocity
        assert not caps.has_retros
        assert not caps.has_burndown

    def test_for_hybrid(self) -> None:
        caps = MethodologyCapabilities.for_methodology(Methodology.HYBRID)
        assert caps.has_sprints
        assert caps.has_backlog
        assert caps.has_milestones
        assert caps.has_epics
        assert caps.has_wip_limits
        assert caps.has_velocity
        assert caps.has_retros
        assert caps.has_burndown

    def test_for_shape_up(self) -> None:
        caps = MethodologyCapabilities.for_methodology(Methodology.SHAPE_UP)
        assert not caps.has_sprints
        assert caps.has_backlog
        assert caps.has_milestones
        assert caps.has_epics
        assert not caps.has_wip_limits
        assert not caps.has_velocity
        assert caps.has_retros
        assert not caps.has_burndown

    def test_frozen(self) -> None:
        caps = MethodologyCapabilities()
        with pytest.raises(AttributeError):
            caps.has_sprints = True  # type: ignore[misc]

    def test_equality_by_value(self) -> None:
        assert MethodologyCapabilities() == MethodologyCapabilities()

    def test_inequality_different_capabilities(self) -> None:
        assert MethodologyCapabilities() != MethodologyCapabilities(has_sprints=True)
