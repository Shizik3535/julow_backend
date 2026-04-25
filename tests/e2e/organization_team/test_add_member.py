"""E2E-тесты: POST /orgs/{org_id}/teams/{team_id}/members/{user_id}."""

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
class TestAddTeamMember:
    """Добавление участника в команду."""

    async def _create_team(self, client, owner) -> str:
        resp = await client.post(
            f"{API}/orgs/{owner['org_id']}/teams",
            json={"name": "Team For Members"},
            headers=auth_headers(owner["access_token"]),
        )
        assert resp.status_code == 201
        return resp.json()["data"]["id"]

    async def test_add_team_member_success(self, client) -> None:
        """200 — добавление участника орг в команду."""
        owner = await create_org_with_owner(client)
        team_id = await self._create_team(client, owner)
        member = await register_and_login(client)
        await add_member_to_org(
            client,
            org_id=owner["org_id"],
            owner_token=owner["access_token"],
            new_member_user_id=member["user_id"],
        )
        resp = await client.post(
            f"{API}/orgs/{owner['org_id']}/teams/{team_id}/members/{member['user_id']}",
            headers=auth_headers(owner["access_token"]),
        )

        assert resp.status_code == 200

    async def test_add_team_member_conflict(self, client) -> None:
        """409 — участник уже в команде."""
        owner = await create_org_with_owner(client)
        team_id = await self._create_team(client, owner)
        member = await register_and_login(client)
        await add_member_to_org(
            client,
            org_id=owner["org_id"],
            owner_token=owner["access_token"],
            new_member_user_id=member["user_id"],
        )
        await client.post(
            f"{API}/orgs/{owner['org_id']}/teams/{team_id}/members/{member['user_id']}",
            headers=auth_headers(owner["access_token"]),
        )
        resp = await client.post(
            f"{API}/orgs/{owner['org_id']}/teams/{team_id}/members/{member['user_id']}",
            headers=auth_headers(owner["access_token"]),
        )
        assert resp.status_code == 409

    async def test_add_team_member_forbidden(self, client) -> None:
        """403 — не-владелец не может добавить участника."""
        owner = await create_org_with_owner(client)
        team_id = await self._create_team(client, owner)
        member = await register_and_login(client)
        await add_member_to_org(
            client,
            org_id=owner["org_id"],
            owner_token=owner["access_token"],
            new_member_user_id=member["user_id"],
        )
        other = await register_and_login(client)
        resp = await client.post(
            f"{API}/orgs/{owner['org_id']}/teams/{team_id}/members/{member['user_id']}",
            headers=auth_headers(other["access_token"]),
        )
        assert resp.status_code == 403

    async def test_add_team_member_not_found(self, client) -> None:
        """404 — команда не найдена."""
        owner = await create_org_with_owner(client)
        resp = await client.post(
            f"{API}/orgs/{owner['org_id']}/teams/{uuid.uuid4()}/members/{uuid.uuid4()}",
            headers=auth_headers(owner["access_token"]),
        )
        assert resp.status_code == 404

    async def test_add_team_member_no_auth(self, client) -> None:
        """401 — без токена авторизации."""
        resp = await client.post(
            f"{API}/orgs/{uuid.uuid4()}/teams/{uuid.uuid4()}/members/{uuid.uuid4()}",
        )
        assert resp.status_code == 401
