"""E2E-тесты: POST /orgs/{org_id}/members."""

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
class TestAddMember:
    """Добавление участника в организацию."""

    async def test_add_member_success(self, client) -> None:
        """201 — владелец добавляет участника."""
        owner = await create_org_with_owner(client)
        member = await register_and_login(client)
        resp = await client.post(
            f"{API}/orgs/{owner['org_id']}/members",
            json={"user_id": member["user_id"]},
            headers=auth_headers(owner["access_token"]),
        )

        assert resp.status_code == 201

    async def test_add_member_conflict(self, client) -> None:
        """409 — повторное добавление уже существующего участника."""
        owner = await create_org_with_owner(client)
        member = await register_and_login(client)
        await add_member_to_org(
            client,
            org_id=owner["org_id"],
            owner_token=owner["access_token"],
            new_member_user_id=member["user_id"],
        )
        resp = await client.post(
            f"{API}/orgs/{owner['org_id']}/members",
            json={"user_id": member["user_id"]},
            headers=auth_headers(owner["access_token"]),
        )
        assert resp.status_code == 409

    async def test_add_member_forbidden(self, client) -> None:
        """403 — не-владелец не может добавить участника."""
        owner = await create_org_with_owner(client)
        other = await register_and_login(client)
        resp = await client.post(
            f"{API}/orgs/{owner['org_id']}/members",
            json={"user_id": other["user_id"]},
            headers=auth_headers(other["access_token"]),
        )
        assert resp.status_code == 403

    async def test_add_member_org_not_found(self, client) -> None:
        """404 — организация не найдена."""
        owner = await create_org_with_owner(client)
        resp = await client.post(
            f"{API}/orgs/{uuid.uuid4()}/members",
            json={"user_id": str(uuid.uuid4())},
            headers=auth_headers(owner["access_token"]),
        )
        assert resp.status_code == 404

    async def test_add_member_no_auth(self, client) -> None:
        """401 — без токена авторизации."""
        resp = await client.post(
            f"{API}/orgs/{uuid.uuid4()}/members",
            json={"user_id": str(uuid.uuid4())},
        )
        assert resp.status_code == 401

    async def test_add_member_validation(self, client) -> None:
        """422 — отсутствует user_id."""
        owner = await create_org_with_owner(client)
        resp = await client.post(
            f"{API}/orgs/{owner['org_id']}/members",
            json={},
            headers=auth_headers(owner["access_token"]),
        )
        assert resp.status_code == 422
