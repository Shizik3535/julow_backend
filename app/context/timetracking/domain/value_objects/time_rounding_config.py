from __future__ import annotations

from dataclasses import dataclass

from app.shared.domain.base_value_object import ValueObject
from app.context.timetracking.domain.value_objects.time_rounding_rule import TimeRoundingRule
from app.context.timetracking.domain.value_objects.rounding_apply_to import RoundingApplyTo


@dataclass(frozen=True)
class TimeRoundingConfig(ValueObject):
    """
    Конфигурация округления времени.

    Атрибуты:
        rule: Правило округления.
        apply_to: К каким записям применять.
    """

    rule: TimeRoundingRule = TimeRoundingRule.NONE
    apply_to: RoundingApplyTo = RoundingApplyTo.ALL
