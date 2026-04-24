"""Пример e2e-теста."""

import pytest


@pytest.mark.e2e
class TestHealthEndpoint:
    async def test_openapi_json_available(self, client) -> None:
        """Проверяет, что OpenAPI схема доступна."""
        response = await client.get("/api/v1/openapi.json")
        assert response.status_code == 200

    async def test_docs_available(self, client) -> None:
        """Проверяет, что Swagger UI доступен."""
        response = await client.get("/api/v1/docs")
        assert response.status_code == 200
