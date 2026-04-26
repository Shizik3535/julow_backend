"""E2E-тесты: GET /orgs/invitations/mine — Мои приглашения в организации."""

import uuid

import pytest
from httpx import AsyncClient

from tests.e2e.conftest import API, auth_headers, register_and_login

MEMBER_ROLE_ID = "00000000-0000-0000-0000-000000000014"


@pytest.mark.e2e
class TestGetMyOrgInvitations:
    """GET /orgs/invitations/mine."""

    async def test_my_invitations_pending(self, client, org_with_owner) -> None:
        """200 — пользователь видит свои PENDING приглашения."""
        owner = org_with_owner
        invitee = await register_and_login(client)

        # Отправляем приглашение на email invitee
        await client.post(
            f"{API}/orgs/{owner['org_id']}/invitations/email",
            json={"email": invitee["email"], "role_id": MEMBER_ROLE_ID},
            headers=auth_headers(owner["access_token"])
        )

        # Invitee запрашивает свои приглашения
        resp = await client.get(
            f"{API}/orgs/invitations/mine",
            headers=auth_headers(invitee["access_token"])
        )
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert isinstance(data, list)
        assert any(inv.get("email") == invitee["email"] for inv in data)

    async def test_my_invitations_no_auth(self, client) -> None:
        """401 — без токена."""
        resp = await client.get(f"{API}/orgs/invitations/mine")
        assert resp.status_code == 401

    async def test_my_invitations_empty(self, client, org_with_owner) -> None:
        """200 — нет приглашений для пользователя."""
        user = await register_and_login(client)
        resp = await client.get(
            f"{API}/orgs/invitations/mine",
            headers=auth_headers(user["access_token"])
        )
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert isinstance(data, list)

    async def test_my_invitations_with_status_filter(self, client, org_with_owner) -> None:
        """200 — фильтр по статусу pending."""
        owner = org_with_owner
        invitee = await register_and_login(client)

        await client.post(
            f"{API}/orgs/{owner['org_id']}/invitations/email",
            json={"email": invitee["email"], "role_id": MEMBER_ROLE_ID},
            headers=auth_headers(owner["access_token"])
        )

        resp = await client.get(
            f"{API}/orgs/invitations/mine",
            params={"status": "pending"},
            headers=auth_headers(invitee["access_token"])
        )
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert all(inv.get("status") == "pending" for inv in data)

    async def test_my_invitations_pagination(self, client, org_with_owner) -> None:
        """200 — пагинация offset/limit."""
        owner = org_with_owner
        invitee = await register_and_login(client)

        # Создаём несколько приглашений
        for i in range(3):
            await client.post(
                f"{API}/orgs/{owner['org_id']}/invitations/email",
                json={"email": invitee["email"], "role_id": MEMBER_ROLE_ID},
                headers=auth_headers(owner["access_token"])
            )

        resp = await client.get(
            f"{API}/orgs/invitations/mine",
            params={"offset": 0, "limit": 1},
            headers=auth_headers(invitee["access_token"])
        )
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert len(data) <= 1
