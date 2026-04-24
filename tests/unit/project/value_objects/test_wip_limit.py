"""Unit-тесты для WIPLimit (Project BC)."""

import pytest

from app.shared.domain.exceptions import ValidationException
from app.context.project.domain.value_objects.wip_limit import WIPLimit


@pytest.mark.unit
class TestWIPLimit:
    def test_valid_value(self) -> None:
        vo = WIPLimit(value=5)
        assert vo.value == 5

    def test_invalid_value_zero_raises(self) -> None:
        with pytest.raises(ValidationException) as exc_info:
            WIPLimit(value=0)
        assert exc_info.value.field == "wip_limit"

    def test_invalid_value_negative_raises(self) -> None:
        with pytest.raises(ValidationException) as exc_info:
            WIPLimit(value=-1)
        assert exc_info.value.field == "wip_limit"

    def test_frozen(self) -> None:
        vo = WIPLimit(value=5)
        with pytest.raises(AttributeError):
            vo.value = 10  # type: ignore[misc]

    def test_equality_by_value(self) -> None:
        assert WIPLimit(value=5) == WIPLimit(value=5)

    def test_inequality_different_value(self) -> None:
        assert WIPLimit(value=5) != WIPLimit(value=10)

    def test_str_representation(self) -> None:
        assert str(WIPLimit(value=5)) == "5"
