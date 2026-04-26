import pytest
from httpx import AsyncClient

from tests.e2e.conftest import (
    API,
    auth_headers,
    create_workspace_with_owner,
    register_and_login,
    register_user,
    add_ws_member_with_role,
)


@pytest.mark.e2e
class TestAddWorkspaceMember:
    """POST /workspaces/{ws_id}/members — Добавить участника (members.write)."""

    async def test_add_member_success_owner(self, client: AsyncClient):
        """201 — owner добавляет участника."""
        ws = await create_workspace_with_owner(client)
        new_user = await register_user(client)
        # Находим роль member
        roles_resp = await client.get(
            f"{API}/workspaces/{ws['ws_id']}/roles",
            params={"system_only": True},
            headers=auth_headers(ws["access_token"]),
        )
        roles = roles_resp.json()["items"]
        member_role_id = next(r["id"] for r in roles if r["name"] == "member")
        resp = await client.post(
            f"{API}/workspaces/{ws['ws_id']}/members",
            json={"user_id": new_user["user_id"], "role_id": member_role_id},
            headers=auth_headers(ws["access_token"]),
        )
        assert resp.status_code == 201

    async def test_add_member_success_admin(self, client: AsyncClient):
        """201 — admin добавляет (через members.*)."""
        ws = await create_workspace_with_owner(client)
        admin = await register_and_login(client)
        await add_ws_member_with_role(
            client,
            ws_id=ws["ws_id"],
            owner_token=ws["access_token"],
            new_member_user_id=admin["user_id"],
            role_name="admin",
        )
        new_user = await register_user(client)
        result = await add_ws_member_with_role(
            client,
            ws_id=ws["ws_id"],
            owner_token=admin["access_token"],
            new_member_user_id=new_user["user_id"],
            role_name="member",
        )
        assert result["response"].status_code == 201

    async def test_add_member_no_auth(self, client: AsyncClient):
        """401 — без токена."""
        ws = await create_workspace_with_owner(client)
        resp = await client.post(
            f"{API}/workspaces/{ws['ws_id']}/members",
            json={"user_id": "some-user", "role_id": "some-role"},
        )
        assert resp.status_code == 401

    async def test_add_member_forbidden_manager(self, client: AsyncClient):
        """403 — manager (нет members.write)."""
        ws = await create_workspace_with_owner(client)
        manager = await register_and_login(client)
        await add_ws_member_with_role(
            client,
            ws_id=ws["ws_id"],
            owner_token=ws["access_token"],
            new_member_user_id=manager["user_id"],
            role_name="manager",
        )
        new_user = await register_user(client)
        resp = await client.post(
            f"{API}/workspaces/{ws['ws_id']}/members",
            json={"user_id": new_user["user_id"], "role_id": "some-role"},
            headers=auth_headers(manager["access_token"]),
        )
        assert resp.status_code == 403

    async def test_add_member_forbidden_member(self, client: AsyncClient):
        """403 — member (нет members.write)."""
        ws = await create_workspace_with_owner(client)
        member = await register_and_login(client)
        await add_ws_member_with_role(
            client,
            ws_id=ws["ws_id"],
            owner_token=ws["access_token"],
            new_member_user_id=member["user_id"],
            role_name="member",
        )
        new_user = await register_user(client)
        resp = await client.post(
            f"{API}/workspaces/{ws['ws_id']}/members",
            json={"user_id": new_user["user_id"], "role_id": "some-role"},
            headers=auth_headers(member["access_token"]),
        )
        assert resp.status_code == 403

    async def test_add_member_not_found_workspace(self, client: AsyncClient):
        """404 — несуществующий workspace."""
        user = await register_and_login(client)
        resp = await client.post(
            f"{API}/workspaces/00000000-0000-0000-0000-000000000000/members",
            json={"user_id": user["user_id"], "role_id": "some-role"},
            headers=auth_headers(user["access_token"]),
        )
        assert resp.status_code == 404

    async def test_add_member_conflict_duplicate(self, client: AsyncClient):
        """409 — участник уже существует."""
        ws = await create_workspace_with_owner(client)
        new_user = await register_user(client)
        result = await add_ws_member_with_role(
            client,
            ws_id=ws["ws_id"],
            owner_token=ws["access_token"],
            new_member_user_id=new_user["user_id"],
            role_name="member",
        )
        assert result["response"].status_code == 201
        # Повторное добавление
        resp = await client.post(
            f"{API}/workspaces/{ws['ws_id']}/members",
            json={"user_id": new_user["user_id"], "role_id": result["role_id"]},
            headers=auth_headers(ws["access_token"]),
        )
        assert resp.status_code == 409

    async def test_add_member_validation_missing_user_id(self, client: AsyncClient):
        """422 — отсутствует user_id."""
        ws = await create_workspace_with_owner(client)
        resp = await client.post(
            f"{API}/workspaces/{ws['ws_id']}/members",
            json={"role_id": "some-role"},
            headers=auth_headers(ws["access_token"]),
        )
        assert resp.status_code == 422
