"""E2E-тесты: DELETE /admin/users/{user_id}/roles/{role_id}."""

import uuid

import pytest

from tests.e2e.conftest import API, auth_headers, register_and_login, register_admin_and_login


@pytest.mark.e2e
class TestRemoveRole:
    """Снятие роли с пользователя."""

    async def test_remove_role_success(self, client) -> None:
        """200 — роль снята (admin назначает, затем снимает)."""
        admin = await register_admin_and_login(client)
        target = await register_and_login(client)
        admin_headers = auth_headers(admin["access_token"])
        target_headers = auth_headers(target["access_token"])

        roles_resp = await client.get(f"{API}/account/roles", headers=target_headers)
        roles = roles_resp.json()["data"]
        if len(roles) < 2:
            pytest.skip("Недостаточно ролей для теста снятия")

        # Назначаем вторую роль
        role_id = roles[1]["id"]
        assign_resp = await client.post(
            f"{API}/admin/users/{target['user_id']}/roles/{role_id}",
            headers=admin_headers,
        )
        assert assign_resp.status_code == 200

        # Снимаем назначенную роль
        resp = await client.delete(
            f"{API}/admin/users/{target['user_id']}/roles/{role_id}",
            headers=admin_headers,
        )
        assert resp.status_code == 200

    async def test_remove_role_no_auth(self, client) -> None:
        """401 — без токена авторизации."""
        fake_uid = str(uuid.uuid4())
        fake_rid = str(uuid.uuid4())
        resp = await client.delete(
            f"{API}/admin/users/{fake_uid}/roles/{fake_rid}"
        )
        assert resp.status_code == 401

    async def test_remove_role_forbidden(self, client) -> None:
        """403 — обычный пользователь не может снимать роли."""
        user = await register_and_login(client)
        headers = auth_headers(user["access_token"])

        fake_uid = str(uuid.uuid4())
        fake_rid = str(uuid.uuid4())
        resp = await client.delete(
            f"{API}/admin/users/{fake_uid}/roles/{fake_rid}",
            headers=headers,
        )
        assert resp.status_code == 403
