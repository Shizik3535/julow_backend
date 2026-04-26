"""E2E-тесты: POST /orgs/{org_id}/transfer-ownership."""

import uuid

import pytest

from tests.e2e.conftest import (
    API,
    add_member_to_org,
    auth_headers,
    register_and_login
)


@pytest.mark.e2e
class TestTransferOwnership:
    """Передача владения организацией."""
    async def test_transfer_ownership_forbidden(self, client, org_with_owner) -> None:
        """403 — не-владелец не может передать владение."""
        owner = org_with_owner
        other = await register_and_login(client)
        resp = await client.post(
            f"{API}/orgs/{owner['org_id']}/transfer-ownership",
            json={"from_id": owner["user_id"], "to_id": other["user_id"]},
            headers=auth_headers(other["access_token"])
        )
        assert resp.status_code == 403
    async def test_transfer_ownership_not_found(self, client, org_with_owner) -> None:
        """404 — организация не найдена."""
        owner = org_with_owner
        resp = await client.post(
            f"{API}/orgs/{uuid.uuid4()}/transfer-ownership",
            json={"from_id": owner["user_id"], "to_id": str(uuid.uuid4())},
            headers=auth_headers(owner["access_token"])
        )
        assert resp.status_code == 404
    async def test_transfer_ownership_no_auth(self, client) -> None:
        """401 — без токена авторизации."""
        resp = await client.post(
            f"{API}/orgs/{uuid.uuid4()}/transfer-ownership",
            json={"from_id": str(uuid.uuid4()), "to_id": str(uuid.uuid4())}
        )
        assert resp.status_code == 401
    async def test_transfer_ownership_success(self, client, org_with_owner) -> None:
        """200 — владелец передаёт владение участнику организации."""
        owner = org_with_owner
        member = await register_and_login(client)
        await add_member_to_org(
            client,
            org_id=owner["org_id"],
            owner_token=owner["access_token"],
            new_member_user_id=member["user_id"]
        )
        resp = await client.post(
            f"{API}/orgs/{owner['org_id']}/transfer-ownership",
            json={"from_id": owner["user_id"], "to_id": member["user_id"]},
            headers=auth_headers(owner["access_token"])
        )

        assert resp.status_code == 200
