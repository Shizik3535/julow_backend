"""E2E-тесты: PATCH /orgs/{org_id}/storage/{storage_id}."""

import uuid

import pytest

from tests.e2e.conftest import API, auth_headers, create_org_with_owner, register_and_login


@pytest.mark.e2e
class TestUpdateStorage:
    """Обновление хранилища."""

    async def _create_storage(self, client, owner) -> str:
        resp = await client.post(
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
        assert resp.status_code == 201
        return resp.json()["data"]["id"]

    async def test_update_storage_success(self, client) -> None:
        """200 — обновление конфигурации/квоты."""
        owner = await create_org_with_owner(client)
        storage_id = await self._create_storage(client, owner)
        resp = await client.patch(
            f"{API}/orgs/{owner['org_id']}/storage/{storage_id}",
            json={"max_bytes": 10737418240},
            headers=auth_headers(owner["access_token"]),
        )

        assert resp.status_code == 200

    async def test_update_storage_forbidden(self, client) -> None:
        """403 — не-владелец не может обновить хранилище."""
        owner = await create_org_with_owner(client)
        storage_id = await self._create_storage(client, owner)
        other = await register_and_login(client)
        resp = await client.patch(
            f"{API}/orgs/{owner['org_id']}/storage/{storage_id}",
            json={"max_bytes": 999},
            headers=auth_headers(other["access_token"]),
        )
        assert resp.status_code == 403

    async def test_update_storage_not_found(self, client) -> None:
        """404 — хранилище не найдено."""
        owner = await create_org_with_owner(client)
        resp = await client.patch(
            f"{API}/orgs/{owner['org_id']}/storage/{uuid.uuid4()}",
            json={"max_bytes": 999},
            headers=auth_headers(owner["access_token"]),
        )
        assert resp.status_code == 404

    async def test_update_storage_no_auth(self, client) -> None:
        """401 — без токена авторизации."""
        resp = await client.patch(
            f"{API}/orgs/{uuid.uuid4()}/storage/{uuid.uuid4()}",
            json={"max_bytes": 999},
        )
        assert resp.status_code == 401
