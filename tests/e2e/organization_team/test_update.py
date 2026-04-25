"""E2E-тесты: PATCH /orgs/{org_id}/teams/{team_id}."""

import uuid

import pytest

from tests.e2e.conftest import API, auth_headers, create_org_with_owner, register_and_login


@pytest.mark.e2e
class TestUpdateTeam:
    """Обновление команды."""

    async def _create_team(self, client, owner) -> str:
        resp = await client.post(
            f"{API}/orgs/{owner['org_id']}/teams",
            json={"name": "Team To Update"},
            headers=auth_headers(owner["access_token"]),
        )
        assert resp.status_code == 201
        return resp.json()["data"]["id"]

    async def test_update_team_success(self, client) -> None:
        """200 — обновление имени/описания команды."""
        owner = await create_org_with_owner(client)
        team_id = await self._create_team(client, owner)
        resp = await client.patch(
            f"{API}/orgs/{owner['org_id']}/teams/{team_id}",
            json={"name": "Updated Team", "description": "New description"},
            headers=auth_headers(owner["access_token"]),
        )

        assert resp.status_code == 200

    async def test_update_team_forbidden(self, client) -> None:
        """403 — не-владелец не может обновить команду."""
        owner = await create_org_with_owner(client)
        team_id = await self._create_team(client, owner)
        other = await register_and_login(client)
        resp = await client.patch(
            f"{API}/orgs/{owner['org_id']}/teams/{team_id}",
            json={"name": "Hacked Team"},
            headers=auth_headers(other["access_token"]),
        )
        assert resp.status_code == 403

    async def test_update_team_not_found(self, client) -> None:
        """404 — команда не найдена."""
        owner = await create_org_with_owner(client)
        resp = await client.patch(
            f"{API}/orgs/{owner['org_id']}/teams/{uuid.uuid4()}",
            json={"name": "Ghost"},
            headers=auth_headers(owner["access_token"]),
        )
        assert resp.status_code == 404

    async def test_update_team_no_auth(self, client) -> None:
        """401 — без токена авторизации."""
        resp = await client.patch(
            f"{API}/orgs/{uuid.uuid4()}/teams/{uuid.uuid4()}",
            json={"name": "NoAuth"},
        )
        assert resp.status_code == 401
