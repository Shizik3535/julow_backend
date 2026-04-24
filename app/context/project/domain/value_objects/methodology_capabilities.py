from __future__ import annotations

from dataclasses import dataclass

from app.shared.domain.base_value_object import ValueObject
from app.context.project.domain.value_objects.methodology import Methodology


@dataclass(frozen=True)
class MethodologyCapabilities(ValueObject):
    """
    Возможности методологии.

    Определяет доступный функционал для методологии проекта.

    Атрибуты:
        has_sprints: Поддержка спринтов.
        has_backlog: Поддержка бэклога.
        has_milestones: Поддержка milestones.
        has_epics: Поддержка эпиков.
        has_wip_limits: Поддержка WIP-лимитов.
        has_velocity: Поддержка метрики velocity.
        has_retros: Поддержка ретроспектив.
        has_burndown: Поддержка burndown-чарта.
    """

    has_sprints: bool = False
    has_backlog: bool = False
    has_milestones: bool = False
    has_epics: bool = False
    has_wip_limits: bool = False
    has_velocity: bool = False
    has_retros: bool = False
    has_burndown: bool = False

    @classmethod
    def for_methodology(cls, methodology: Methodology) -> MethodologyCapabilities:
        """Возвращает предустановленные capabilities для методологии."""
        _CAPABILITIES: dict[Methodology, dict[str, bool]] = {
            Methodology.KANBAN: dict(
                has_milestones=True, has_epics=True, has_wip_limits=True,
            ),
            Methodology.SCRUM: dict(
                has_sprints=True, has_backlog=True, has_epics=True,
                has_velocity=True, has_retros=True, has_burndown=True,
            ),
            Methodology.WATERFALL: dict(
                has_milestones=True, has_epics=True,
            ),
            Methodology.HYBRID: dict(
                has_sprints=True, has_backlog=True, has_milestones=True,
                has_epics=True, has_wip_limits=True, has_velocity=True,
                has_retros=True, has_burndown=True,
            ),
            Methodology.SHAPE_UP: dict(
                has_backlog=True, has_milestones=True, has_epics=True,
                has_retros=True,
            ),
        }
        return cls(**_CAPABILITIES.get(methodology, {}))
