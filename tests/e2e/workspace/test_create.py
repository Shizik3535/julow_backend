import pytest
from httpx import AsyncClient

from tests.e2e.conftest import (
    API,
    auth_headers,
    create_workspace_with_owner,
    create_workspace_in_org,
    register_and_login,
    register_user,
    add_member_to_org,
    create_organization,
)


@pytest.mark.e2e
class TestCreateWorkspace:
    """POST /workspaces/ — Создание workspace."""

    async def test_create_standalone_success(self, client: AsyncClient):
        """201 — автономный workspace (без org_id), без проверки permission."""
        user = await register_and_login(client)
        resp = await client.post(
            f"{API}/workspaces/",
            json={"name": "My Standalone WS"},
            headers=auth_headers(user["access_token"]),
        )
        assert resp.status_code == 201
        data = resp.json()["data"]
        assert data["name"] == "My Standalone WS"
        assert data["id"]

    async def test_create_inside_org_success(self, client: AsyncClient):
        """201 — workspace внутри организации (владелец org)."""
        org_ws = await create_workspace_in_org(client)
        assert org_ws["ws_id"]

    async def test_create_inside_org_forbidden(self, client: AsyncClient):
        """403 — пользователь без workspaces.create в организации."""
        # Создаём организацию и workspace
        org_owner = await register_and_login(client)
        org = await create_organization(client, token=org_owner["access_token"])

        # Другой пользователь, не участник org
        stranger = await register_and_login(client)
        resp = await client.post(
            f"{API}/workspaces/",
            json={"name": "Forbidden WS", "organization_id": org["org_id"]},
            headers=auth_headers(stranger["access_token"]),
        )
        assert resp.status_code == 403

    async def test_create_no_auth(self, client: AsyncClient):
        """401 — без токена."""
        resp = await client.post(
            f"{API}/workspaces/",
            json={"name": "No Auth WS"},
        )
        assert resp.status_code == 401

    async def test_create_validation_short_name(self, client: AsyncClient):
        """422 — name < 3 символов."""
        user = await register_and_login(client)
        resp = await client.post(
            f"{API}/workspaces/",
            json={"name": "AB"},
            headers=auth_headers(user["access_token"]),
        )
        assert resp.status_code == 422

    async def test_create_validation_missing_body(self, client: AsyncClient):
        """422 — отсутствует тело."""
        user = await register_and_login(client)
        resp = await client.post(
            f"{API}/workspaces/",
            headers=auth_headers(user["access_token"]),
        )
        assert resp.status_code == 422
