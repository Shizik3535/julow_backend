"""E2E-тесты: GET /orgs."""

import pytest

from tests.e2e.conftest import API, auth_headers, create_org_with_owner


@pytest.mark.e2e
class TestSearchOrganizations:
    """Поиск организаций."""

    async def test_search_organizations_success(self, client) -> None:
        """200 — пагинированный список организаций."""
        owner = await create_org_with_owner(client)
        resp = await client.get(
            f"{API}/orgs/",
            headers=auth_headers(owner["access_token"]),
        )

        assert resp.status_code == 200
        body = resp.json()
        assert "items" in body
        assert "total" in body

    async def test_search_organizations_contains_created(self, client) -> None:
        """200 — созданная организация появляется в списке."""
        owner = await create_org_with_owner(client)
        resp = await client.get(
            f"{API}/orgs/",
            headers=auth_headers(owner["access_token"]),
        )

        assert resp.status_code == 200
        items = resp.json()["items"]
        org_ids = [item["id"] for item in items]
        assert owner["org_id"] in org_ids

    async def test_search_organizations_no_auth(self, client) -> None:
        """401 — без токена авторизации."""
        resp = await client.get(f"{API}/orgs/")
        assert resp.status_code == 401
