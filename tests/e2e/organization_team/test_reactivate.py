"""E2E-тесты: POST /orgs/{org_id}/teams/{team_id}/reactivate."""

import uuid

import pytest

from tests.e2e.conftest import API, auth_headers, create_org_with_owner, register_and_login


@pytest.mark.e2e
class TestReactivateTeam:
    """Реактивация команды."""

    async def _create_and_deactivate_team(self, client, owner) -> str:
        resp = await client.post(
            f"{API}/orgs/{owner['org_id']}/teams",
            json={"name": "Team To Reactivate"},
            headers=auth_headers(owner["access_token"]),
        )
        team_id = resp.json()["data"]["id"]
        await client.post(
            f"{API}/orgs/{owner['org_id']}/teams/{team_id}/deactivate",
            headers=auth_headers(owner["access_token"]),
        )
        return team_id

    async def test_reactivate_team_success(self, client) -> None:
        """200 — реактивация деактивированной команды."""
        owner = await create_org_with_owner(client)
        team_id = await self._create_and_deactivate_team(client, owner)
        resp = await client.post(
            f"{API}/orgs/{owner['org_id']}/teams/{team_id}/reactivate",
            headers=auth_headers(owner["access_token"]),
        )

        assert resp.status_code == 200

    async def test_reactivate_team_already_active(self, client) -> None:
        """409 — реактивация активной команды."""
        owner = await create_org_with_owner(client)
        resp_create = await client.post(
            f"{API}/orgs/{owner['org_id']}/teams",
            json={"name": "Active Team"},
            headers=auth_headers(owner["access_token"]),
        )
        team_id = resp_create.json()["data"]["id"]
        resp = await client.post(
            f"{API}/orgs/{owner['org_id']}/teams/{team_id}/reactivate",
            headers=auth_headers(owner["access_token"]),
        )
        assert resp.status_code == 409

    async def test_reactivate_team_forbidden(self, client) -> None:
        """403 — не-владелец не может реактивировать."""
        owner = await create_org_with_owner(client)
        team_id = await self._create_and_deactivate_team(client, owner)
        other = await register_and_login(client)
        resp = await client.post(
            f"{API}/orgs/{owner['org_id']}/teams/{team_id}/reactivate",
            headers=auth_headers(other["access_token"]),
        )
        assert resp.status_code == 403

    async def test_reactivate_team_not_found(self, client) -> None:
        """404 — команда не найдена."""
        owner = await create_org_with_owner(client)
        resp = await client.post(
            f"{API}/orgs/{owner['org_id']}/teams/{uuid.uuid4()}/reactivate",
            headers=auth_headers(owner["access_token"]),
        )
        assert resp.status_code == 404

    async def test_reactivate_team_no_auth(self, client) -> None:
        """401 — без токена авторизации."""
        resp = await client.post(f"{API}/orgs/{uuid.uuid4()}/teams/{uuid.uuid4()}/reactivate")
        assert resp.status_code == 401
