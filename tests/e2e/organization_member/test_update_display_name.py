"""E2E-тесты: PATCH /orgs/{org_id}/members/{user_id}/display-name."""

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
class TestUpdateMemberDisplayName:
    """Обновление отображаемого имени участника."""

    async def test_update_display_name_success(self, client) -> None:
        """200 — владелец обновляет отображаемое имя."""
        owner = await create_org_with_owner(client)
        member = await register_and_login(client)
        await add_member_to_org(
            client,
            org_id=owner["org_id"],
            owner_token=owner["access_token"],
            new_member_user_id=member["user_id"],
        )
        resp = await client.patch(
            f"{API}/orgs/{owner['org_id']}/members/{member['user_id']}/display-name",
            json={"display_name": "New Display Name"},
            headers=auth_headers(owner["access_token"]),
        )

        assert resp.status_code == 200

    async def test_update_display_name_forbidden(self, client) -> None:
        """403 — не-владелец не может обновить имя."""
        owner = await create_org_with_owner(client)
        member = await register_and_login(client)
        await add_member_to_org(
            client,
            org_id=owner["org_id"],
            owner_token=owner["access_token"],
            new_member_user_id=member["user_id"],
        )
        other = await register_and_login(client)
        resp = await client.patch(
            f"{API}/orgs/{owner['org_id']}/members/{member['user_id']}/display-name",
            json={"display_name": "Hacked"},
            headers=auth_headers(other["access_token"]),
        )
        assert resp.status_code == 403

    async def test_update_display_name_not_found(self, client) -> None:
        """404 — участник не найден."""
        owner = await create_org_with_owner(client)
        resp = await client.patch(
            f"{API}/orgs/{owner['org_id']}/members/{uuid.uuid4()}/display-name",
            json={"display_name": "Ghost"},
            headers=auth_headers(owner["access_token"]),
        )
        assert resp.status_code == 404

    async def test_update_display_name_no_auth(self, client) -> None:
        """401 — без токена авторизации."""
        resp = await client.patch(
            f"{API}/orgs/{uuid.uuid4()}/members/{uuid.uuid4()}/display-name",
            json={"display_name": "NoAuth"},
        )
        assert resp.status_code == 401
