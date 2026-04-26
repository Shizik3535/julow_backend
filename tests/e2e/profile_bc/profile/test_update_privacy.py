"""E2E-тесты: PUT /profile/me/privacy."""

import pytest

from tests.e2e.conftest import API


@pytest.mark.e2e
class TestUpdatePrivacy:
    """Обновление настроек приватности."""

    async def test_update_privacy_success(self, auth_client) -> None:
        """200 — настройки обновлены."""
        resp = await auth_client.put(
            f"{API}/profile/me/privacy",
            json={
                "profile_visibility": "organization_only",
                "online_status_visibility": "everyone",
                "activity_tracking_consent": "granted",
            }
        )
        assert resp.status_code == 200

    async def test_update_privacy_private(self, auth_client) -> None:
        """200 — приватный профиль."""
        resp = await auth_client.put(
            f"{API}/profile/me/privacy",
            json={
                "profile_visibility": "private",
                "online_status_visibility": "nobody",
                "activity_tracking_consent": "denied",
            }
        )
        assert resp.status_code == 200

    async def test_update_privacy_no_auth(self, client) -> None:
        """401 — без токена авторизации."""
        resp = await client.put(
            f"{API}/profile/me/privacy",
            json={
                "profile_visibility": "public",
                "online_status_visibility": "everyone",
                "activity_tracking_consent": "granted",
            }
        )
        assert resp.status_code == 401
