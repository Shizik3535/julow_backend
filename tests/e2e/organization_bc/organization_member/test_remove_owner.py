"""E2E-тесты: DELETE /orgs/{org_id}/owners/{user_id}."""

import uuid

import pytest

from tests.e2e.conftest import (
    API,
    add_member_to_org,
    auth_headers,
    register_and_login
)


@pytest.mark.e2e
class TestRemoveOwner:
    """Удаление со-владельца."""

    async def test_remove_owner_success(self, client, org_with_owner) -> None:
        """200 — удаление со-владельца (остаётся ≥1 владелец)."""
        owner = org_with_owner
        member = await register_and_login(client)
        await add_member_to_org(
            client,
            org_id=owner["org_id"],
            owner_token=owner["access_token"],
            new_member_user_id=member["user_id"]
        )
        # Добавляем со-владельца
        await client.post(
            f"{API}/orgs/{owner['org_id']}/owners",
            json={"user_id": member["user_id"]},
            headers=auth_headers(owner["access_token"])
        )
        # Удаляем со-владельца
        resp = await client.delete(
            f"{API}/orgs/{owner['org_id']}/owners/{member['user_id']}",
            headers=auth_headers(owner["access_token"])
        )

        assert resp.status_code == 200

    async def test_remove_owner_last_owner(self, client, org_with_owner) -> None:
        """409 — нельзя удалить последнего владельца."""
        owner = org_with_owner
        resp = await client.delete(
            f"{API}/orgs/{owner['org_id']}/owners/{owner['user_id']}",
            headers=auth_headers(owner["access_token"])
        )
        assert resp.status_code == 409

    async def test_remove_owner_forbidden(self, client, org_with_owner) -> None:
        """403 — не-владелец не может удалить со-владельца."""
        owner = org_with_owner
        member = await register_and_login(client)
        await add_member_to_org(
            client,
            org_id=owner["org_id"],
            owner_token=owner["access_token"],
            new_member_user_id=member["user_id"]
        )
        resp = await client.delete(
            f"{API}/orgs/{owner['org_id']}/owners/{owner['user_id']}",
            headers=auth_headers(member["access_token"])
        )
        assert resp.status_code == 403

    async def test_remove_owner_not_found(self, client, org_with_owner) -> None:
        """404 — организация не найдена."""
        owner = org_with_owner
        resp = await client.delete(
            f"{API}/orgs/{uuid.uuid4()}/owners/{uuid.uuid4()}",
            headers=auth_headers(owner["access_token"])
        )
        assert resp.status_code == 404

    async def test_remove_owner_no_auth(self, client) -> None:
        """401 — без токена авторизации."""
        resp = await client.delete(f"{API}/orgs/{uuid.uuid4()}/owners/{uuid.uuid4()}")
        assert resp.status_code == 401
