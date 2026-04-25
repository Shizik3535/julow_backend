"""E2E-тесты: DELETE /orgs/{org_id}/roles/{role_id}."""

import uuid

import pytest

from tests.e2e.conftest import API, auth_headers, create_org_with_owner, register_and_login


@pytest.mark.e2e
class TestDeleteRole:
    """Удаление роли."""

    async def _create_custom_role(self, client, owner) -> str:
        """Создаёт кастомную роль и возвращает её ID."""
        resp = await client.post(
            f"{API}/orgs/{owner['org_id']}/roles",
            json={
                "name": "Role To Delete",
                "permissions": ["members:read"],
                "scope": "org",
            },
            headers=auth_headers(owner["access_token"]),
        )
        assert resp.status_code == 201
        return resp.json()["data"]["id"]

    async def test_delete_role_success(self, client) -> None:
        """200 — удаление кастомной роли."""
        owner = await create_org_with_owner(client)
        role_id = await self._create_custom_role(client, owner)
        resp = await client.delete(
            f"{API}/orgs/{owner['org_id']}/roles/{role_id}",
            headers=auth_headers(owner["access_token"]),
        )

        assert resp.status_code == 200

    async def test_delete_role_system_forbidden(self, client) -> None:
        """409 — нельзя удалить системную роль."""
        owner = await create_org_with_owner(client)
        roles_resp = await client.get(
            f"{API}/orgs/{owner['org_id']}/roles",
            headers=auth_headers(owner["access_token"]),
        )
        system_roles = [r for r in roles_resp.json()["data"] if r.get("is_system")]
        if not system_roles:
            pytest.skip("Нет системных ролей")

        role_id = system_roles[0]["id"]
        resp = await client.delete(
            f"{API}/orgs/{owner['org_id']}/roles/{role_id}",
            headers=auth_headers(owner["access_token"]),
        )
        assert resp.status_code == 409

    async def test_delete_role_forbidden(self, client) -> None:
        """403 — не-владелец не может удалить роль."""
        owner = await create_org_with_owner(client)
        role_id = await self._create_custom_role(client, owner)
        other = await register_and_login(client)
        resp = await client.delete(
            f"{API}/orgs/{owner['org_id']}/roles/{role_id}",
            headers=auth_headers(other["access_token"]),
        )
        assert resp.status_code == 403

    async def test_delete_role_not_found(self, client) -> None:
        """404 — роль не найдена."""
        owner = await create_org_with_owner(client)
        resp = await client.delete(
            f"{API}/orgs/{owner['org_id']}/roles/{uuid.uuid4()}",
            headers=auth_headers(owner["access_token"]),
        )
        assert resp.status_code == 404

    async def test_delete_role_no_auth(self, client) -> None:
        """401 — без токена авторизации."""
        resp = await client.delete(f"{API}/orgs/{uuid.uuid4()}/roles/{uuid.uuid4()}")
        assert resp.status_code == 401
