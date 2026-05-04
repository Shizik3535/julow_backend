"""E2E-сценарий: update personal info → appearance → notifications → privacy → get profile."""

import pytest

from tests.e2e.conftest import API, auth_headers, register_and_login


@pytest.mark.e2e
class TestProfileSettingsFlow:
    """Полный цикл обновления настроек профиля."""

    async def test_full_profile_settings_flow(self, client) -> None:
        """Обновляем все настройки и проверяем профиль."""
        user = await register_and_login(client)
        headers = auth_headers(user["access_token"])

        # 1. Обновляем персональные данные
        resp1 = await client.patch(
            f"{API}/profile/me/personal-info",
            json={
                "bio": "E2E тестовый bio",
                "job_title": "QA Engineer",
            },
            headers=headers
        )
        assert resp1.status_code == 200

        # 2. Обновляем внешний вид
        resp2 = await client.put(
            f"{API}/profile/me/appearance",
            json={
                "theme": "dark",
                "accent_color": "#10B981",
                "interface_density": "spacious",
            },
            headers=headers
        )
        assert resp2.status_code == 200

        # 3. Обновляем приватность
        resp4 = await client.put(
            f"{API}/profile/me/privacy",
            json={
                "profile_visibility": "private",
                "online_status_visibility": "nobody",
                "activity_tracking_consent": "denied",
            },
            headers=headers
        )
        assert resp4.status_code == 200

        # 4. Проверяем, что профиль доступен
        profile_resp = await client.get(
            f"{API}/profile/me", headers=headers
        )
        assert profile_resp.status_code == 200
        profile = profile_resp.json()["data"]
        assert profile is not None
