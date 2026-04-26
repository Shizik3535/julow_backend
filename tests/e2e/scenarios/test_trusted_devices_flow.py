"""E2E-сценарий: add trusted device → get list → remove device."""

import uuid

import pytest

from tests.e2e.conftest import API, auth_headers, register_and_login


@pytest.mark.e2e
class TestTrustedDevicesFlow:
    """Полный цикл доверенных устройств: добавление → просмотр → удаление."""

    async def test_add_get_remove_device(self, client) -> None:
        """add → get (есть в списке) → remove → get (нет в списке)."""
        user = await register_and_login(client)
        headers = auth_headers(user["access_token"])
        fingerprint = uuid.uuid4().hex[:12]

        # 1. Добавляем
        add_resp = await client.post(
            f"{API}/account/security/trusted-devices",
            json={"device_fingerprint": fingerprint},
            headers=headers
        )
        assert add_resp.status_code == 200

        # 2. Проверяем наличие в списке
        list_resp = await client.get(
            f"{API}/account/security/trusted-devices", headers=headers
        )
        assert list_resp.status_code == 200
        devices = list_resp.json()["data"]
        fingerprints = [d.get("device_fingerprint", d.get("fingerprint", "")) for d in devices]
        assert fingerprint in fingerprints

        # 3. Удаляем
        remove_resp = await client.delete(
            f"{API}/account/security/trusted-devices/{fingerprint}",
            headers=headers
        )
        assert remove_resp.status_code == 200

        # 4. Проверяем, что удалено
        list_resp2 = await client.get(
            f"{API}/account/security/trusted-devices", headers=headers
        )
        devices2 = list_resp2.json()["data"]
        fingerprints2 = [d.get("device_fingerprint", d.get("fingerprint", "")) for d in devices2]
        assert fingerprint not in fingerprints2
