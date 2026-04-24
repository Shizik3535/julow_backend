"""Unit-тесты для TrustedDevice."""

from datetime import datetime, timedelta, timezone

import pytest

from app.shared.domain.value_objects.ip_address_vo import IpAddress
from app.context.identity.domain.entities.trusted_device import TrustedDevice
from app.context.identity.domain.value_objects.device_info import DeviceInfo


@pytest.mark.unit
class TestTrustedDevice:
    def test_create_trusted_device(self) -> None:
        device = TrustedDevice(
            device_fingerprint="fp_abc123",
            device_info=DeviceInfo(user_agent="Chrome"),
            ip=IpAddress("192.168.1.1"),
        )
        assert device.device_fingerprint == "fp_abc123"
        assert not device.is_expired()

    def test_expired_device(self) -> None:
        device = TrustedDevice(
            device_fingerprint="fp_abc123",
            device_info=DeviceInfo(user_agent="Chrome"),
            ip=IpAddress("192.168.1.1"),
            expires_at=datetime.now(tz=timezone.utc) - timedelta(hours=1),
        )
        assert device.is_expired()

    def test_not_expired_device(self) -> None:
        device = TrustedDevice(
            device_fingerprint="fp_abc123",
            device_info=DeviceInfo(user_agent="Chrome"),
            ip=IpAddress("192.168.1.1"),
            expires_at=datetime.now(tz=timezone.utc) + timedelta(days=30),
        )
        assert not device.is_expired()
