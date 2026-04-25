"""E2E-тесты: POST /orgs/{org_id}/teams."""

import uuid

import pytest

from tests.e2e.conftest import API, auth_headers, create_org_with_owner, register_and_login


@pytest.mark.e2e
class TestCreateTeam:
    """Создание команды."""

    async def test_create_team_success(self, client) -> None:
        """201 — создание команды."""
        owner = await create_org_with_owner(client)
        resp = await client.post(
            f"{API}/orgs/{owner['org_id']}/teams",
            json={"name": "New Team"},
            headers=auth_headers(owner["access_token"]),
        )

        assert resp.status_code == 201
        data = resp.json()["data"]
        assert data["id"]
        assert data["name"] == "New Team"

    async def test_create_team_forbidden(self, client) -> None:
        """403 — не-владелец не может создать команду."""
        owner = await create_org_with_owner(client)
        other = await register_and_login(client)
        resp = await client.post(
            f"{API}/orgs/{owner['org_id']}/teams",
            json={"name": "Hacked Team"},
            headers=auth_headers(other["access_token"]),
        )
        assert resp.status_code == 403

    async def test_create_team_not_found(self, client) -> None:
        """404 — организация не найдена."""
        owner = await create_org_with_owner(client)
        resp = await client.post(
            f"{API}/orgs/{uuid.uuid4()}/teams",
            json={"name": "Ghost Team"},
            headers=auth_headers(owner["access_token"]),
        )
        assert resp.status_code == 404

    async def test_create_team_no_auth(self, client) -> None:
        """401 — без токена авторизации."""
        resp = await client.post(
            f"{API}/orgs/{uuid.uuid4()}/teams",
            json={"name": "NoAuth Team"},
        )
        assert resp.status_code == 401

    async def test_create_team_validation(self, client) -> None:
        """422 — отсутствует name."""
        owner = await create_org_with_owner(client)
        resp = await client.post(
            f"{API}/orgs/{owner['org_id']}/teams",
            json={},
            headers=auth_headers(owner["access_token"]),
        )
        assert resp.status_code == 422
