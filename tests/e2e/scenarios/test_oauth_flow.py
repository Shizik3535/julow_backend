"""E2E-сценарий: link OAuth → get links → unlink OAuth."""

import pytest

from tests.e2e.conftest import API, auth_headers, register_and_login


@pytest.mark.e2e
class TestOAuthFlow:
    """Полный цикл OAuth: привязка → просмотр → отвязка."""

    async def test_link_get_unlink_oauth(self, client) -> None:
        """link → get (есть в списке) → unlink → get (нет в списке)."""
        user = await register_and_login(client)
        headers = auth_headers(user["access_token"])

        # 1. Привязываем
        link_resp = await client.post(
            f"{API}/account/security/oauth/link",
            json={
                "provider": "oauth_github",
                "authorization_code": "test-code-github-12345",
                "redirect_uri": "https://app.example.com/oauth/callback",
            },
            headers=headers,
        )
        assert link_resp.status_code == 200

        # 2. Проверяем наличие в списке
        list_resp = await client.get(
            f"{API}/account/security/oauth", headers=headers
        )
        assert list_resp.status_code == 200
        providers = [item.get("provider", "") for item in list_resp.json()["data"]]
        assert "oauth_github" in providers

        # 3. Отвязываем
        unlink_resp = await client.delete(
            f"{API}/account/security/oauth/oauth_github",
            headers=headers,
        )
        assert unlink_resp.status_code == 200

        # 4. Проверяем отсутствие
        list_resp2 = await client.get(
            f"{API}/account/security/oauth", headers=headers
        )
        providers2 = [item.get("provider", "") for item in list_resp2.json()["data"]]
        assert "oauth_github" not in providers2
