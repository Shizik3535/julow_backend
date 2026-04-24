from __future__ import annotations

from dataclasses import dataclass

from app.shared.domain.base_value_object import ValueObject
from app.context.security.domain.value_objects.data_region import DataRegion


@dataclass(frozen=True)
class DataResidency(ValueObject):
    """Конфигурация data residency."""

    region: DataRegion = DataRegion.EU_CENTRAL
    country_code: str = "DE"
