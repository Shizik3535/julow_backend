"""E2E-тесты: GET /account/roles."""

import pytest

from tests.e2e.conftest import API


@pytest.mark.e2e
class TestGetRoles:
    """Получение списка ролей."""

    async def test_get_roles_success(self, auth_client) -> None:
        """200 — список ролей."""
        resp = await auth_client.get(f"{API}/account/roles")

        assert resp.status_code == 200
        data = resp.json()["data"]
        assert isinstance(data, list)

    async def test_get_roles_with_filter(self, auth_client) -> None:
        """200 — фильтрация по имени."""
        resp = await auth_client.get(
            f"{API}/account/roles", params={"name": "user"}
        )
        assert resp.status_code == 200

    async def test_get_roles_with_pagination(self, auth_client) -> None:
        """200 — пагинация."""
        resp = await auth_client.get(
            f"{API}/account/roles", params={"offset": 0, "limit": 10}
        )
        assert resp.status_code == 200

    async def test_get_roles_no_auth(self, client) -> None:
        """401 — без токена авторизации."""
        resp = await client.get(f"{API}/account/roles")
        assert resp.status_code == 401
