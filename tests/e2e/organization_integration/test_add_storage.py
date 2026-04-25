"""E2E-тесты: POST /orgs/{org_id}/storage."""

import uuid

import pytest

from tests.e2e.conftest import API, auth_headers, create_org_with_owner, register_and_login


@pytest.mark.e2e
class TestAddStorage:
    """Добавление хранилища."""

    async def test_add_storage_success(self, client) -> None:
        """201 — добавление хранилища (S3-конфиг)."""
        owner = await create_org_with_owner(client)
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
        data = resp.json()["data"]
        assert data["id"]

    async def test_add_storage_forbidden(self, client) -> None:
        """403 — не-владелец не может добавить хранилище."""
        owner = await create_org_with_owner(client)
        other = await register_and_login(client)
        resp = await client.post(
            f"{API}/orgs/{owner['org_id']}/storage",
            json={
                "provider": "aws_s3",
                "endpoint": "https://s3.example.com",
                "bucket": "hack-bucket",
                "region": "us-east-1",
                "access_key": "hack-key",
            },
            headers=auth_headers(other["access_token"]),
        )
        assert resp.status_code == 403

    async def test_add_storage_not_found(self, client) -> None:
        """404 — организация не найдена."""
        owner = await create_org_with_owner(client)
        resp = await client.post(
            f"{API}/orgs/{uuid.uuid4()}/storage",
            json={
                "provider": "aws_s3",
                "endpoint": "https://s3.example.com",
                "bucket": "ghost-bucket",
                "region": "us-east-1",
                "access_key": "ghost-key",
            },
            headers=auth_headers(owner["access_token"]),
        )
        assert resp.status_code == 404

    async def test_add_storage_no_auth(self, client) -> None:
        """401 — без токена авторизации."""
        resp = await client.post(
            f"{API}/orgs/{uuid.uuid4()}/storage",
            json={
                "provider": "aws_s3",
                "endpoint": "https://s3.example.com",
                "bucket": "noauth-bucket",
                "region": "us-east-1",
                "access_key": "noauth-key",
            },
        )
        assert resp.status_code == 401

    async def test_add_storage_validation(self, client) -> None:
        """422 — отсутствуют обязательные поля."""
        owner = await create_org_with_owner(client)
        resp = await client.post(
            f"{API}/orgs/{owner['org_id']}/storage",
            json={"provider": "aws_s3"},
            headers=auth_headers(owner["access_token"]),
        )
        assert resp.status_code == 422
