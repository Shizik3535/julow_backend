"""E2E-сценарий: приглашения в организацию."""

import uuid

import pytest

from tests.e2e.conftest import API, auth_headers, register_and_login

MEMBER_ROLE_ID = "00000000-0000-0000-0000-000000000014"


@pytest.mark.e2e
class TestInvitationFlow:
    """Сценарий: send_invitation → get_invitations → accept → get_members | decline."""

    async def test_invitation_accept_flow(self, client, org_with_owner) -> None:
        """Приглашение → принятие → участник в организации."""
        owner = org_with_owner
        org_id = owner["org_id"]
        token = owner["access_token"]

        # 1. Отправка приглашения
        invite_email = f"accept-{uuid.uuid4().hex[:8]}@example.com"
        resp = await client.post(
            f"{API}/orgs/{org_id}/invitations/email",
            json={"email": invite_email, "role_id": MEMBER_ROLE_ID},
            headers=auth_headers(token)
        )
        assert resp.status_code == 201
        invitation_id = resp.json()["data"]["id"]

        # 2. Проверка в списке приглашений
        resp = await client.get(
            f"{API}/orgs/{org_id}/invitations",
            headers=auth_headers(token)
        )
        assert resp.status_code == 200
        invite_ids = [inv["id"] for inv in resp.json()["data"]]
        assert invitation_id in invite_ids

        # 3. Принятие приглашения другим пользователем
        accepter = await register_and_login(client)
        resp = await client.post(
            f"{API}/orgs/invitations/{invitation_id}/accept",
            headers=auth_headers(accepter["access_token"])
        )
        assert resp.status_code == 200

        # 4. Пользователь стал участником организации
        resp = await client.get(
            f"{API}/orgs/{org_id}/members",
            headers=auth_headers(token)
        )
        member_ids = [m["user_id"] for m in resp.json()["data"]]
        assert accepter["user_id"] in member_ids

    async def test_invitation_decline_flow(self, client, org_with_owner) -> None:
        """Приглашение → отклонение → пользователь НЕ в организации."""
        owner = org_with_owner
        org_id = owner["org_id"]
        token = owner["access_token"]

        # 1. Отправка приглашения
        invite_email = f"decline-{uuid.uuid4().hex[:8]}@example.com"
        resp = await client.post(
            f"{API}/orgs/{org_id}/invitations/email",
            json={"email": invite_email, "role_id": MEMBER_ROLE_ID},
            headers=auth_headers(token)
        )
        invitation_id = resp.json()["data"]["id"]

        # 2. Отклонение приглашения пользователем с тем же email
        decliner = await register_and_login(client, email=invite_email)
        resp = await client.post(
            f"{API}/orgs/invitations/{invitation_id}/decline",
            headers=auth_headers(decliner["access_token"])
        )
        assert resp.status_code == 200

        # 3. Пользователь НЕ стал участником
        resp = await client.get(
            f"{API}/orgs/{org_id}/members",
            headers=auth_headers(token)
        )
        member_ids = [m["user_id"] for m in resp.json()["data"]]
        assert decliner["user_id"] not in member_ids
