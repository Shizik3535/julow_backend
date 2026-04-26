"""E2E-тесты: GET /account/security/trusted-devices."""

import pytest

from tests.e2e.conftest import API


@pytest.mark.e2e
class TestGetTrustedDevices:
    """Список доверенных устройств."""

    async def test_get_trusted_devices_success(self, auth_client) -> None:
        """200 — возвращает список (может быть пустым)."""
        resp = await auth_client.get(f"{API}/account/security/trusted-devices")

        assert resp.status_code == 200
        data = resp.json()["data"]
        assert isinstance(data, list)

    async def test_get_trusted_devices_no_auth(self, client) -> None:
        """401 — без токена авторизации."""
        resp = await client.get(f"{API}/account/security/trusted-devices")
        assert resp.status_code == 401
