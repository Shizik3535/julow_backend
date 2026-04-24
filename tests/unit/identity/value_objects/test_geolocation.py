"""Unit-тесты для Geolocation."""

import pytest

from app.shared.domain.exceptions import ValidationException
from app.context.identity.domain.value_objects.geolocation import Geolocation


@pytest.mark.unit
class TestGeolocation:
    def test_valid_geolocation_with_coords(self) -> None:
        geo = Geolocation(country="Russia", city="Moscow", latitude=55.75, longitude=37.62)
        assert geo.country == "Russia"
        assert geo.latitude == 55.75

    def test_geolocation_without_coords(self) -> None:
        geo = Geolocation(country="Russia", city="Moscow")
        assert geo.latitude is None
        assert geo.longitude is None

    def test_latitude_without_longitude_raises(self) -> None:
        with pytest.raises(ValidationException) as exc_info:
            Geolocation(latitude=55.75)
        assert exc_info.value.field == "geolocation"

    def test_longitude_without_latitude_raises(self) -> None:
        with pytest.raises(ValidationException):
            Geolocation(longitude=37.62)

    def test_latitude_out_of_range_raises(self) -> None:
        with pytest.raises(ValidationException) as exc_info:
            Geolocation(latitude=91.0, longitude=0.0)
        assert exc_info.value.field == "latitude"

    def test_longitude_out_of_range_raises(self) -> None:
        with pytest.raises(ValidationException) as exc_info:
            Geolocation(latitude=0.0, longitude=181.0)
        assert exc_info.value.field == "longitude"

    def test_boundary_latitude(self) -> None:
        geo = Geolocation(latitude=90.0, longitude=0.0)
        assert geo.latitude == 90.0

    def test_boundary_longitude(self) -> None:
        geo = Geolocation(latitude=0.0, longitude=180.0)
        assert geo.longitude == 180.0
