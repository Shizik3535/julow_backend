"""E2E-тесты: POST /orgs/{org_id}/teams/{team_id}/deactivate."""

import uuid

import pytest

from tests.e2e.conftest import API, auth_headers, register_and_login


@pytest.mark.e2e
class TestDeactivateTeam:
    """Деактивация команды."""

    async def _create_team(self, client, owner) -> str:
        resp = await client.post(
            f"{API}/orgs/{owner['org_id']}/teams",
            json={"name": "Team To Deactivate"},
            headers=auth_headers(owner["access_token"])
        )
        assert resp.status_code == 201
        return resp.json()["data"]["id"]

    async def test_deactivate_team_success(self, client, org_with_owner) -> None:
        """200 — деактивация команды."""
        owner = org_with_owner
        team_id = await self._create_team(client, owner)
        resp = await client.post(
            f"{API}/orgs/{owner['org_id']}/teams/{team_id}/deactivate",
            headers=auth_headers(owner["access_token"])
        )

        assert resp.status_code == 200

    async def test_deactivate_team_already_deactivated(self, client, org_with_owner) -> None:
        """409 — повторная деактивация."""
        owner = org_with_owner
        team_id = await self._create_team(client, owner)
        await client.post(
            f"{API}/orgs/{owner['org_id']}/teams/{team_id}/deactivate",
            headers=auth_headers(owner["access_token"])
        )
        resp = await client.post(
            f"{API}/orgs/{owner['org_id']}/teams/{team_id}/deactivate",
            headers=auth_headers(owner["access_token"])
        )
        assert resp.status_code == 409

    async def test_deactivate_team_forbidden(self, client, org_with_owner) -> None:
        """403 — не-владелец не может деактивировать."""
        owner = org_with_owner
        team_id = await self._create_team(client, owner)
        other = await register_and_login(client)
        resp = await client.post(
            f"{API}/orgs/{owner['org_id']}/teams/{team_id}/deactivate",
            headers=auth_headers(other["access_token"])
        )
        assert resp.status_code == 403

    async def test_deactivate_team_not_found(self, client, org_with_owner) -> None:
        """404 — команда не найдена."""
        owner = org_with_owner
        resp = await client.post(
            f"{API}/orgs/{owner['org_id']}/teams/{uuid.uuid4()}/deactivate",
            headers=auth_headers(owner["access_token"])
        )
        assert resp.status_code == 404

    async def test_deactivate_team_no_auth(self, client) -> None:
        """401 — без токена авторизации."""
        resp = await client.post(f"{API}/orgs/{uuid.uuid4()}/teams/{uuid.uuid4()}/deactivate")
        assert resp.status_code == 401
