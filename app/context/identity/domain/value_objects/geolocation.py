from __future__ import annotations

from dataclasses import dataclass

from app.shared.domain.base_value_object import ValueObject
from app.shared.domain.exceptions import ValidationException


@dataclass(frozen=True)
class Geolocation(ValueObject):
    """
    Value Object для геолокации.

    Определяется на инфраструктурном уровне (GeoIP-сервис)
    и передаётся в домен как готовый Value Object.

    Атрибуты:
        country: Название страны.
        city: Название города.
        latitude: Широта.
        longitude: Долгота.
    """

    country: str | None = None
    city: str | None = None
    latitude: float | None = None
    longitude: float | None = None

    def __post_init__(self) -> None:
        has_coords = self.latitude is not None or self.longitude is not None
        if has_coords and (self.latitude is None or self.longitude is None):
            raise ValidationException(
                field="geolocation",
                message="Широта и долгота должны быть указаны вместе",
            )
        if self.latitude is not None and not -90 <= self.latitude <= 90:
            raise ValidationException(
                field="latitude",
                message=f"Широта должна быть в диапазоне [-90, 90]: {self.latitude}",
            )
        if self.longitude is not None and not -180 <= self.longitude <= 180:
            raise ValidationException(
                field="longitude",
                message=f"Долгота должна быть в диапазоне [-180, 180]: {self.longitude}",
            )
