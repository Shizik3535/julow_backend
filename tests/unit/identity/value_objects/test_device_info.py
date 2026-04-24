"""Unit-тесты для DeviceInfo."""

import pytest

from app.shared.domain.exceptions import ValidationException
from app.context.identity.domain.value_objects.device_info import DeviceInfo


@pytest.mark.unit
class TestDeviceInfo:
    def test_valid_device_info(self) -> None:
        di = DeviceInfo(user_agent="Mozilla/5.0", os="Windows", browser="Chrome", device_type="desktop")
        assert di.user_agent == "Mozilla/5.0"
        assert di.os == "Windows"

    def test_empty_user_agent_raises(self) -> None:
        with pytest.raises(ValidationException) as exc_info:
            DeviceInfo(user_agent="")
        assert exc_info.value.field == "user_agent"

    def test_whitespace_user_agent_raises(self) -> None:
        with pytest.raises(ValidationException):
            DeviceInfo(user_agent="   ")

    def test_optional_fields_default_none(self) -> None:
        di = DeviceInfo(user_agent="Mozilla/5.0")
        assert di.os is None
        assert di.browser is None
        assert di.device_type is None

    def test_equality(self) -> None:
        di1 = DeviceInfo(user_agent="Mozilla/5.0", os="Linux")
        di2 = DeviceInfo(user_agent="Mozilla/5.0", os="Linux")
        assert di1 == di2
