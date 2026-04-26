"""E2E-тесты: PUT /profile/me/appearance."""

import pytest

from tests.e2e.conftest import API


@pytest.mark.e2e
class TestUpdateAppearance:
    """Обновление настроек внешнего вида."""

    async def test_update_appearance_success(self, auth_client) -> None:
        """200 — настройки обновлены."""
        resp = await auth_client.put(
            f"{API}/profile/me/appearance",
            json={
                "theme": "dark",
                "accent_color": "#6366F1",
                "interface_density": "comfortable",
            }
        )
        assert resp.status_code == 200

    async def test_update_appearance_light_theme(self, auth_client) -> None:
        """200 — светлая тема."""
        resp = await auth_client.put(
            f"{API}/profile/me/appearance",
            json={
                "theme": "light",
                "accent_color": "#EF4444",
                "interface_density": "compact",
            }
        )
        assert resp.status_code == 200

    async def test_update_appearance_invalid_color(self, auth_client) -> None:
        """422 — невалидный формат цвета."""
        resp = await auth_client.put(
            f"{API}/profile/me/appearance",
            json={
                "theme": "dark",
                "accent_color": "not-a-color",
                "interface_density": "comfortable",
            }
        )
        assert resp.status_code == 422

    async def test_update_appearance_no_auth(self, client) -> None:
        """401 — без токена авторизации."""
        resp = await client.put(
            f"{API}/profile/me/appearance",
            json={
                "theme": "dark",
                "accent_color": "#6366F1",
                "interface_density": "comfortable",
            }
        )
        assert resp.status_code == 401
