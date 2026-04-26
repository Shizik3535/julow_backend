import pytest
from httpx import AsyncClient

from tests.e2e.conftest import (
    API,
    auth_headers,
    create_workspace_with_owner,
    register_user,
    add_ws_member_with_role,
)


@pytest.mark.e2e
class TestWorkspaceMemberFlow:
    """Сценарий: add_member → get_members → change_role → deactivate → reactivate → remove_member."""

    async def test_full_member_flow(self, client: AsyncClient):
        ws = await create_workspace_with_owner(client)
        h = auth_headers(ws["access_token"])
        ws_id = ws["ws_id"]

        # 1. Add member
        new_user = await register_user(client)
        result = await add_ws_member_with_role(
            client,
            ws_id=ws_id,
            owner_token=ws["access_token"],
            new_member_user_id=new_user["user_id"],
            role_name="member",
        )
        assert result["response"].status_code == 201

        # 2. Get members
        resp = await client.get(f"{API}/workspaces/{ws_id}/members", headers=h)
        assert resp.status_code == 200
        items = resp.json()["items"]
        assert len(items) >= 2

        # 3. Change role to manager
        roles_resp = await client.get(
            f"{API}/workspaces/{ws_id}/roles",
            params={"system_only": True},
            headers=h,
        )
        roles = roles_resp.json()["items"]
        manager_role_id = next(r["id"] for r in roles if r["name"] == "manager")
        resp = await client.patch(
            f"{API}/workspaces/{ws_id}/members/{new_user['user_id']}/role",
            json={"new_role_id": manager_role_id},
            headers=h,
        )
        assert resp.status_code == 200

        # 4. Deactivate
        resp = await client.post(
            f"{API}/workspaces/{ws_id}/members/{new_user['user_id']}/deactivate",
            headers=h,
        )
        assert resp.status_code == 200

        # 5. Reactivate
        resp = await client.post(
            f"{API}/workspaces/{ws_id}/members/{new_user['user_id']}/reactivate",
            headers=h,
        )
        assert resp.status_code == 200

        # 6. Remove member
        resp = await client.delete(
            f"{API}/workspaces/{ws_id}/members/{new_user['user_id']}",
            headers=h,
        )
        assert resp.status_code == 200
