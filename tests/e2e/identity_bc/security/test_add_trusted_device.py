"""E2E-тесты: POST /account/security/trusted-devices."""

import uuid

import pytest

from tests.e2e.conftest import API


@pytest.mark.e2e
class TestAddTrustedDevice:
    """Добавление доверенного устройства."""

    async def test_add_trusted_device_success(self, auth_client) -> None:
        """200 — устройство добавлено."""
        fingerprint = uuid.uuid4().hex[:12]
        resp = await auth_client.post(
            f"{API}/account/security/trusted-devices",
            json={"device_fingerprint": fingerprint}
        )
        assert resp.status_code == 200

    async def test_add_trusted_device_with_expiry(self, auth_client) -> None:
        """200 — устройство добавлено с expires_at."""
        fingerprint = uuid.uuid4().hex[:12]
        resp = await auth_client.post(
            f"{API}/account/security/trusted-devices",
            json={
                "device_fingerprint": fingerprint,
                "expires_at": "2027-01-01T00:00:00Z",
            }
        )
        assert resp.status_code == 200

    async def test_add_trusted_device_no_auth(self, client) -> None:
        """401 — без токена авторизации."""
        resp = await client.post(
            f"{API}/account/security/trusted-devices",
            json={"device_fingerprint": "abc123"}
        )
        assert resp.status_code == 401
