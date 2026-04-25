"""E2E-тесты: GET /orgs/{org_id}/teams/{team_id}."""

import uuid

import pytest

from tests.e2e.conftest import API, auth_headers, create_org_with_owner


@pytest.mark.e2e
class TestGetTeam:
    """Получение команды по ID."""

    async def _create_team(self, client, owner) -> str:
        resp = await client.post(
            f"{API}/orgs/{owner['org_id']}/teams",
            json={"name": "Test Team"},
            headers=auth_headers(owner["access_token"]),
        )
        assert resp.status_code == 201
        return resp.json()["data"]["id"]

    async def test_get_team_success(self, client) -> None:
        """200 — данные созданной команды."""
        owner = await create_org_with_owner(client)
        team_id = await self._create_team(client, owner)
        resp = await client.get(
            f"{API}/orgs/{owner['org_id']}/teams/{team_id}",
            headers=auth_headers(owner["access_token"]),
        )

        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["id"] == team_id
        assert data["name"] == "Test Team"

    async def test_get_team_not_found(self, client) -> None:
        """404 — команда не найдена."""
        owner = await create_org_with_owner(client)
        resp = await client.get(
            f"{API}/orgs/{owner['org_id']}/teams/{uuid.uuid4()}",
            headers=auth_headers(owner["access_token"]),
        )
        assert resp.status_code == 404

    async def test_get_team_no_auth(self, client) -> None:
        """401 — без токена авторизации."""
        resp = await client.get(f"{API}/orgs/{uuid.uuid4()}/teams/{uuid.uuid4()}")
        assert resp.status_code == 401
