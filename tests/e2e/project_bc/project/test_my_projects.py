"""E2E-тесты: GET /projects/mine, GET /projects/ — Мои проекты и поиск."""

import pytest
from httpx import AsyncClient

from tests.e2e.conftest import (
    API,
    auth_headers,
    create_project,
    register_and_login
)


@pytest.mark.e2e
class TestMyProjects:
    """Мои проекты и поиск проектов."""

    async def test_get_my_projects_success(self, client: AsyncClient, project_owner):
        """200 — возвращает проекты текущего пользователя."""
        proj = project_owner
        resp = await client.get(
            f"{API}/projects/mine",
            headers=auth_headers(proj["access_token"])
        )
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert isinstance(data, list)
        assert len(data) >= 1

    async def test_get_my_projects_no_auth(self, client: AsyncClient):
        """401 — без токена."""
        resp = await client.get(f"{API}/projects/mine")
        assert resp.status_code == 401

    async def test_get_my_projects_empty(self, client: AsyncClient):
        """200 — нет проектов у пользователя."""
        user = await register_and_login(client)
        resp = await client.get(
            f"{API}/projects/mine",
            headers=auth_headers(user["access_token"])
        )
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert isinstance(data, list)

    async def test_search_projects_success(self, client: AsyncClient, project_owner):
        """200 — поиск проектов с фильтрацией."""
        proj = project_owner
        resp = await client.get(
            f"{API}/projects/",
            params={"query": proj["project_name"]},
            headers=auth_headers(proj["access_token"])
        )
        assert resp.status_code == 200
        items = resp.json()["items"]
        assert isinstance(items, list)

    async def test_search_projects_no_auth(self, client: AsyncClient):
        """401 — без токена."""
        resp = await client.get(f"{API}/projects/")
        assert resp.status_code == 401
