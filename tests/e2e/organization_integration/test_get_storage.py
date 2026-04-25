"""E2E-тесты: GET /orgs/{org_id}/storage."""

import uuid

import pytest

from tests.e2e.conftest import API, auth_headers, create_org_with_owner


@pytest.mark.e2e
class TestGetStorage:
    """Получение хранилища организации."""

    async def test_get_storage_not_found_initially(self, client) -> None:
        """404 — хранилище ещё не добавлено."""
        owner = await create_org_with_owner(client)
        resp = await client.get(
            f"{API}/orgs/{owner['org_id']}/storage",
            headers=auth_headers(owner["access_token"]),
        )
        assert resp.status_code == 404

    async def test_get_storage_success(self, client) -> None:
        """200 — после добавления хранилища возвращает данные."""
        owner = await create_org_with_owner(client)
        await client.post(
            f"{API}/orgs/{owner['org_id']}/storage",
            json={
                "provider": "aws_s3",
                "endpoint": "https://s3.example.com",
                "bucket": "test-bucket",
                "region": "us-east-1",
                "access_key": "test-access-key",
            },
            headers=auth_headers(owner["access_token"]),
        )
        resp = await client.get(
            f"{API}/orgs/{owner['org_id']}/storage",
            headers=auth_headers(owner["access_token"]),
        )

        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["id"]

    async def test_get_storage_no_auth(self, client) -> None:
        """401 — без токена авторизации."""
        resp = await client.get(f"{API}/orgs/{uuid.uuid4()}/storage")
        assert resp.status_code == 401
