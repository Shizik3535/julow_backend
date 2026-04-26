"""E2E-тесты: GET /workspaces/invitations/mine — Мои приглашения в workspace."""

import pytest
from httpx import AsyncClient

from tests.e2e.conftest import (
    API,
    auth_headers,
    register_and_login
)


def _member_role_id(roles_resp):
    items = roles_resp.json()["items"]
    return next(r["id"] for r in items if r["name"] == "member")


@pytest.mark.e2e
class TestGetMyWorkspaceInvitations:
    """GET /workspaces/invitations/mine."""

    async def test_my_invitations_pending(self, client: AsyncClient, workspace_owner) -> None:
        """200 — пользователь видит свои PENDING приглашения."""
        ws = workspace_owner
        invitee = await register_and_login(client)

        roles_resp = await client.get(
            f"{API}/workspaces/{ws['ws_id']}/roles",
            params={"system_only": True},
            headers=auth_headers(ws["access_token"])
        )
        role_id = _member_role_id(roles_resp)

        # Отправляем приглашение на email invitee
        await client.post(
            f"{API}/workspaces/{ws['ws_id']}/invitations/email",
            json={"email": invitee["email"], "role_id": role_id},
            headers=auth_headers(ws["access_token"])
        )

        # Invitee запрашивает свои приглашения
        resp = await client.get(
            f"{API}/workspaces/invitations/mine",
            headers=auth_headers(invitee["access_token"])
        )
        assert resp.status_code == 200
        items = resp.json()["items"]
        assert isinstance(items, list)
        assert any(inv.get("email") == invitee["email"] for inv in items)

    async def test_my_invitations_no_auth(self, client: AsyncClient) -> None:
        """401 — без токена."""
        resp = await client.get(f"{API}/workspaces/invitations/mine")
        assert resp.status_code == 401

    async def test_my_invitations_empty(self, client: AsyncClient) -> None:
        """200 — нет приглашений для пользователя."""
        user = await register_and_login(client)
        resp = await client.get(
            f"{API}/workspaces/invitations/mine",
            headers=auth_headers(user["access_token"])
        )
        assert resp.status_code == 200
        items = resp.json()["items"]
        assert isinstance(items, list)

    async def test_my_invitations_with_status_filter(self, client: AsyncClient, workspace_owner) -> None:
        """200 — фильтр по статусу pending."""
        ws = workspace_owner
        invitee = await register_and_login(client)

        roles_resp = await client.get(
            f"{API}/workspaces/{ws['ws_id']}/roles",
            params={"system_only": True},
            headers=auth_headers(ws["access_token"])
        )
        role_id = _member_role_id(roles_resp)

        await client.post(
            f"{API}/workspaces/{ws['ws_id']}/invitations/email",
            json={"email": invitee["email"], "role_id": role_id},
            headers=auth_headers(ws["access_token"])
        )

        resp = await client.get(
            f"{API}/workspaces/invitations/mine",
            params={"status": "pending"},
            headers=auth_headers(invitee["access_token"])
        )
        assert resp.status_code == 200
        items = resp.json()["items"]
        assert all(inv.get("status") == "pending" for inv in items)

    async def test_my_invitations_pagination(self, client: AsyncClient, workspace_owner) -> None:
        """200 — пагинация offset/limit."""
        ws = workspace_owner
        invitee = await register_and_login(client)

        roles_resp = await client.get(
            f"{API}/workspaces/{ws['ws_id']}/roles",
            params={"system_only": True},
            headers=auth_headers(ws["access_token"])
        )
        role_id = _member_role_id(roles_resp)

        for i in range(3):
            await client.post(
                f"{API}/workspaces/{ws['ws_id']}/invitations/email",
                json={"email": invitee["email"], "role_id": role_id},
                headers=auth_headers(ws["access_token"])
            )

        resp = await client.get(
            f"{API}/workspaces/invitations/mine",
            params={"offset": 0, "limit": 1},
            headers=auth_headers(invitee["access_token"])
        )
        assert resp.status_code == 200
        items = resp.json()["items"]
        assert len(items) <= 1
