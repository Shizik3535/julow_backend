"""E2E-тесты: PUT /profile/me/notifications."""

import pytest

from tests.e2e.conftest import API


@pytest.mark.e2e
class TestUpdateNotifications:
    """Обновление настроек уведомлений."""

    async def test_update_notifications_success(self, auth_client) -> None:
        """200 — настройки обновлены."""
        resp = await auth_client.put(
            f"{API}/profile/me/notifications",
            json={
                "type_preferences": [
                    {
                        "notification_type": "task_assigned",
                        "is_enabled": True,
                        "channels": [
                            {"channel": "in_app", "is_enabled": True},
                            {"channel": "email", "is_enabled": True},
                            {"channel": "push", "is_enabled": False},
                            {"channel": "sms", "is_enabled": False},
                        ],
                    },
                ],
            },
        )
        assert resp.status_code == 200

    async def test_update_notifications_empty_preferences(self, auth_client) -> None:
        """200 — пустой список предпочтений."""
        resp = await auth_client.put(
            f"{API}/profile/me/notifications",
            json={"type_preferences": []},
        )
        assert resp.status_code == 200

    async def test_update_notifications_no_auth(self, client) -> None:
        """401 — без токена авторизации."""
        resp = await client.put(
            f"{API}/profile/me/notifications",
            json={"type_preferences": []},
        )
        assert resp.status_code == 401
