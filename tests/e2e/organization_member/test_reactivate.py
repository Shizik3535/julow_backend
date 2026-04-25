"""E2E-тесты: POST /orgs/{org_id}/members/{user_id}/reactivate."""

import uuid

import pytest

from tests.e2e.conftest import (
    API,
    add_member_to_org,
    auth_headers,
    create_org_with_owner,
    register_and_login,
)


@pytest.mark.e2e
class TestReactivateMember:
    """Реактивация участника."""

    async def test_reactivate_member_success(self, client) -> None:
        """200 — реактивация деактивированного участника."""
        owner = await create_org_with_owner(client)
        member = await register_and_login(client)
        await add_member_to_org(
            client,
            org_id=owner["org_id"],
            owner_token=owner["access_token"],
            new_member_user_id=member["user_id"],
        )
        await client.post(
            f"{API}/orgs/{owner['org_id']}/members/{member['user_id']}/deactivate",
            headers=auth_headers(owner["access_token"]),
        )
        resp = await client.post(
            f"{API}/orgs/{owner['org_id']}/members/{member['user_id']}/reactivate",
            headers=auth_headers(owner["access_token"]),
        )

        assert resp.status_code == 200

    async def test_reactivate_member_already_active(self, client) -> None:
        """409 — реактивация активного участника."""
        owner = await create_org_with_owner(client)
        member = await register_and_login(client)
        await add_member_to_org(
            client,
            org_id=owner["org_id"],
            owner_token=owner["access_token"],
            new_member_user_id=member["user_id"],
        )
        resp = await client.post(
            f"{API}/orgs/{owner['org_id']}/members/{member['user_id']}/reactivate",
            headers=auth_headers(owner["access_token"]),
        )
        assert resp.status_code == 409

    async def test_reactivate_member_forbidden(self, client) -> None:
        """403 — не-владелец не может реактивировать."""
        owner = await create_org_with_owner(client)
        member = await register_and_login(client)
        await add_member_to_org(
            client,
            org_id=owner["org_id"],
            owner_token=owner["access_token"],
            new_member_user_id=member["user_id"],
        )
        other = await register_and_login(client)
        resp = await client.post(
            f"{API}/orgs/{owner['org_id']}/members/{member['user_id']}/reactivate",
            headers=auth_headers(other["access_token"]),
        )
        assert resp.status_code == 403

    async def test_reactivate_member_not_found(self, client) -> None:
        """404 — участник не найден."""
        owner = await create_org_with_owner(client)
        resp = await client.post(
            f"{API}/orgs/{owner['org_id']}/members/{uuid.uuid4()}/reactivate",
            headers=auth_headers(owner["access_token"]),
        )
        assert resp.status_code == 404

    async def test_reactivate_member_no_auth(self, client) -> None:
        """401 — без токена авторизации."""
        resp = await client.post(
            f"{API}/orgs/{uuid.uuid4()}/members/{uuid.uuid4()}/reactivate",
        )
        assert resp.status_code == 401
