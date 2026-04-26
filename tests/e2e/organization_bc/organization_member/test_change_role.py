"""E2E-тесты: PATCH /orgs/{org_id}/members/{user_id}/role."""

import uuid

import pytest

from tests.e2e.conftest import (
    API,
    add_member_to_org,
    auth_headers,
    register_and_login
)


@pytest.mark.e2e
class TestChangeMemberRole:
    """Изменение роли участника."""

    async def test_change_member_role_success(self, client, org_with_owner) -> None:
        """200 — владелец меняет роль участника."""
        owner = org_with_owner
        member = await register_and_login(client)
        await add_member_to_org(
            client,
            org_id=owner["org_id"],
            owner_token=owner["access_token"],
            new_member_user_id=member["user_id"]
        )
        # Получаем список ролей организации
        roles_resp = await client.get(
            f"{API}/orgs/{owner['org_id']}/roles",
            headers=auth_headers(owner["access_token"])
        )
        roles = roles_resp.json()["data"]
        if len(roles) < 2:
            pytest.skip("Недостаточно ролей для теста")

        new_role_id = roles[1]["id"]
        resp = await client.patch(
            f"{API}/orgs/{owner['org_id']}/members/{member['user_id']}/role",
            json={"new_role_id": new_role_id},
            headers=auth_headers(owner["access_token"])
        )
        assert resp.status_code == 200

    async def test_change_member_role_forbidden(self, client, org_with_owner) -> None:
        """403 — не-владелец не может менять роли."""
        owner = org_with_owner
        member = await register_and_login(client)
        await add_member_to_org(
            client,
            org_id=owner["org_id"],
            owner_token=owner["access_token"],
            new_member_user_id=member["user_id"]
        )
        resp = await client.patch(
            f"{API}/orgs/{owner['org_id']}/members/{owner['user_id']}/role",
            json={"new_role_id": str(uuid.uuid4())},
            headers=auth_headers(member["access_token"])
        )
        assert resp.status_code == 403

    async def test_change_member_role_not_found(self, client, org_with_owner) -> None:
        """404 — участник не найден."""
        owner = org_with_owner
        resp = await client.patch(
            f"{API}/orgs/{owner['org_id']}/members/{uuid.uuid4()}/role",
            json={"new_role_id": str(uuid.uuid4())},
            headers=auth_headers(owner["access_token"])
        )
        assert resp.status_code == 404

    async def test_change_member_role_no_auth(self, client) -> None:
        """401 — без токена авторизации."""
        resp = await client.patch(
            f"{API}/orgs/{uuid.uuid4()}/members/{uuid.uuid4()}/role",
            json={"new_role_id": str(uuid.uuid4())}
        )
        assert resp.status_code == 401
