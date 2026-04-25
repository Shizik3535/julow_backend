"""E2E-тесты: DELETE /orgs/{org_id}/members/{user_id}."""

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
class TestRemoveMember:
    """Удаление участника из организации."""

    async def test_remove_member_success(self, client) -> None:
        """200 — владелец удаляет участника."""
        owner = await create_org_with_owner(client)
        member = await register_and_login(client)
        await add_member_to_org(
            client,
            org_id=owner["org_id"],
            owner_token=owner["access_token"],
            new_member_user_id=member["user_id"],
        )
        resp = await client.delete(
            f"{API}/orgs/{owner['org_id']}/members/{member['user_id']}",
            headers=auth_headers(owner["access_token"]),
        )

        assert resp.status_code == 200

    async def test_remove_member_forbidden(self, client) -> None:
        """403 — не-владелец не может удалить участника."""
        owner = await create_org_with_owner(client)
        member = await register_and_login(client)
        await add_member_to_org(
            client,
            org_id=owner["org_id"],
            owner_token=owner["access_token"],
            new_member_user_id=member["user_id"],
        )
        other = await register_and_login(client)
        resp = await client.delete(
            f"{API}/orgs/{owner['org_id']}/members/{member['user_id']}",
            headers=auth_headers(other["access_token"]),
        )
        assert resp.status_code == 403

    async def test_remove_member_not_found(self, client) -> None:
        """404 — участник не найден."""
        owner = await create_org_with_owner(client)
        resp = await client.delete(
            f"{API}/orgs/{owner['org_id']}/members/{uuid.uuid4()}",
            headers=auth_headers(owner["access_token"]),
        )
        assert resp.status_code == 404

    async def test_remove_member_no_auth(self, client) -> None:
        """401 — без токена авторизации."""
        resp = await client.delete(f"{API}/orgs/{uuid.uuid4()}/members/{uuid.uuid4()}")
        assert resp.status_code == 401
