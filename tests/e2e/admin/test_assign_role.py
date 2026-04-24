"""E2E-тесты: POST /admin/users/{user_id}/roles/{role_id}."""

import uuid

import pytest

from tests.e2e.conftest import API, auth_headers, register_and_login, register_admin_and_login


@pytest.mark.e2e
class TestAssignRole:
    """Назначение роли пользователю."""

    async def test_assign_role_success(self, client) -> None:
        """200 — роль назначена (admin-пользователь)."""
        admin = await register_admin_and_login(client)
        target = await register_and_login(client)
        headers = auth_headers(admin["access_token"])

        # Получаем список ролей
        roles_resp = await client.get(f"{API}/account/roles", headers=auth_headers(target["access_token"]))
        assert roles_resp.status_code == 200
        roles = roles_resp.json()["data"]

        if len(roles) < 2:
            pytest.skip("Недостаточно ролей для теста назначения")

        # Назначаем вторую роль (первая уже назначена при регистрации)
        role_id = roles[1]["id"]
        resp = await client.post(
            f"{API}/admin/users/{target['user_id']}/roles/{role_id}",
            headers=headers,
        )
        assert resp.status_code == 200

    async def test_assign_role_no_auth(self, client) -> None:
        """401 — без токена авторизации."""
        fake_uid = str(uuid.uuid4())
        fake_rid = str(uuid.uuid4())
        resp = await client.post(
            f"{API}/admin/users/{fake_uid}/roles/{fake_rid}"
        )
        assert resp.status_code == 401

    async def test_assign_role_user_not_found(self, client) -> None:
        """404 — пользователь не найден."""
        admin = await register_admin_and_login(client)
        headers = auth_headers(admin["access_token"])

        roles_resp = await client.get(f"{API}/account/roles", headers=headers)
        roles = roles_resp.json()["data"]
        if not roles:
            pytest.skip("Нет ролей в системе")

        fake_uid = str(uuid.uuid4())
        resp = await client.post(
            f"{API}/admin/users/{fake_uid}/roles/{roles[0]['id']}",
            headers=headers,
        )
        assert resp.status_code == 404

    async def test_assign_role_forbidden(self, client) -> None:
        """403 — обычный пользователь не может назначать роли."""
        user = await register_and_login(client)
        headers = auth_headers(user["access_token"])

        fake_uid = str(uuid.uuid4())
        fake_rid = str(uuid.uuid4())
        resp = await client.post(
            f"{API}/admin/users/{fake_uid}/roles/{fake_rid}",
            headers=headers,
        )
        assert resp.status_code == 403
