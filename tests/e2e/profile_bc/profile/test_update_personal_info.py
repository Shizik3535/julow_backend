"""E2E-тесты: PATCH /profile/me/personal-info."""

import pytest

from tests.e2e.conftest import API


@pytest.mark.e2e
class TestUpdatePersonalInfo:
    """Обновление персональных данных профиля."""

    async def test_update_bio(self, auth_client) -> None:
        """200 — bio обновлён."""
        resp = await auth_client.patch(
            f"{API}/profile/me/personal-info",
            json={"bio": "Люблю DDD и чистую архитектуру"}
        )
        assert resp.status_code == 200

    async def test_update_job_title(self, auth_client) -> None:
        """200 — job_title обновлён."""
        resp = await auth_client.patch(
            f"{API}/profile/me/personal-info",
            json={"job_title": "Senior Software Engineer"}
        )
        assert resp.status_code == 200

    async def test_update_both_fields(self, auth_client) -> None:
        """200 — оба поля обновлены."""
        resp = await auth_client.patch(
            f"{API}/profile/me/personal-info",
            json={
                "bio": "Новый bio",
                "job_title": "Tech Lead",
            }
        )
        assert resp.status_code == 200

    async def test_update_no_auth(self, client) -> None:
        """401 — без токена авторизации."""
        resp = await client.patch(
            f"{API}/profile/me/personal-info",
            json={"bio": "test"}
        )
        assert resp.status_code == 401
