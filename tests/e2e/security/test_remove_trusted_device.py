"""E2E-тесты: DELETE /account/security/trusted-devices/{fingerprint}."""

import uuid

import pytest

from tests.e2e.conftest import API, auth_headers, register_and_login


@pytest.mark.e2e
class TestRemoveTrustedDevice:
    """Удаление доверенного устройства."""

    async def test_remove_trusted_device_success(self, client) -> None:
        """200 — устройство удалено (после добавления)."""
        user = await register_and_login(client)
        headers = auth_headers(user["access_token"])
        fingerprint = uuid.uuid4().hex[:12]

        # Добавляем
        add_resp = await client.post(
            f"{API}/account/security/trusted-devices",
            json={"device_fingerprint": fingerprint},
            headers=headers,
        )
        assert add_resp.status_code == 200

        # Удаляем
        resp = await client.delete(
            f"{API}/account/security/trusted-devices/{fingerprint}",
            headers=headers,
        )
        assert resp.status_code == 200

    async def test_remove_trusted_device_no_auth(self, client) -> None:
        """401 — без токена авторизации."""
        resp = await client.delete(
            f"{API}/account/security/trusted-devices/some-fingerprint"
        )
        assert resp.status_code == 401
