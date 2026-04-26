import pytest
from httpx import AsyncClient

from tests.e2e.conftest import (
    API,
    auth_headers,
    register_and_login,
    add_member_to_org,
    create_workspace
)


@pytest.mark.e2e
class TestGetOrgWorkspaces:
    """GET /orgs/{org_id}/workspaces — Список workspace организации (кросс-BC: workspaces.read + is_org_member)."""

    async def test_get_org_workspaces_success_with_permission(self, client: AsyncClient, workspace_in_org):
        """200 — с workspaces.read: возвращает все workspace организации."""
        org_ws = workspace_in_org
        resp = await client.get(
            f"{API}/orgs/{org_ws['org_id']}/workspaces",
            headers=auth_headers(org_ws["access_token"])
        )
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data.get("items"), list)

    async def test_get_org_workspaces_success_member_only(self, client: AsyncClient, org_with_owner):
        """200 — без workspaces.read: только workspace где caller участник."""
        org_owner = org_with_owner
        # Создаём workspace в организации
        await create_workspace(
            client,
            token=org_owner["access_token"],
            organization_id=org_owner["org_id"]
        )
        # Добавляем участника в org (без workspaces.read)
        member = await register_and_login(client)
        await add_member_to_org(
            client,
            org_id=org_owner["org_id"],
            owner_token=org_owner["access_token"],
            new_member_user_id=member["user_id"]
        )
        resp = await client.get(
            f"{API}/orgs/{org_owner['org_id']}/workspaces",
            headers=auth_headers(member["access_token"])
        )
        assert resp.status_code == 200

    async def test_get_org_workspaces_no_auth(self, client: AsyncClient, workspace_in_org):
        """401 — без токена."""
        org_ws = workspace_in_org
        resp = await client.get(f"{API}/orgs/{org_ws['org_id']}/workspaces")
        assert resp.status_code == 401

    async def test_get_org_workspaces_forbidden_not_member(self, client: AsyncClient, workspace_in_org):
        """403 — не член организации."""
        org_ws = workspace_in_org
        stranger = await register_and_login(client)
        resp = await client.get(
            f"{API}/orgs/{org_ws['org_id']}/workspaces",
            headers=auth_headers(stranger["access_token"])
        )
        assert resp.status_code == 403

    async def test_get_org_workspaces_not_found(self, client: AsyncClient):
        """404 — организация не найдена."""
        user = await register_and_login(client)
        resp = await client.get(
            f"{API}/orgs/00000000-0000-0000-0000-000000000000/workspaces",
            headers=auth_headers(user["access_token"])
        )
        assert resp.status_code == 404
