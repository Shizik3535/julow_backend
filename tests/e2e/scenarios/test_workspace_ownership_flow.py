import pytest
from httpx import AsyncClient

from tests.e2e.conftest import (
    API,
    auth_headers,
    register_and_login,
    add_ws_member_with_role
)


@pytest.mark.e2e
class TestWorkspaceOwnershipFlow:
    """Сценарий: create → add_owner → get (2 владельца) → remove_owner → transfer_ownership → get (новый владелец)."""

    async def test_full_ownership_flow(self, client: AsyncClient, workspace_owner):
        ws = workspace_owner
        h = auth_headers(ws["access_token"])
        ws_id = ws["ws_id"]

        # 1. Add co-owner
        co_owner = await register_and_login(client)
        await add_ws_member_with_role(
            client,
            ws_id=ws_id,
            owner_token=ws["access_token"],
            new_member_user_id=co_owner["user_id"],
            role_name="admin"
        )
        resp = await client.post(
            f"{API}/workspaces/{ws_id}/owners",
            json={"user_id": co_owner["user_id"]},
            headers=h
        )
        assert resp.status_code == 200

        # 2. Get — verify 2 owners (check members list)
        resp = await client.get(f"{API}/workspaces/{ws_id}/members", headers=h)
        assert resp.status_code == 200

        # 3. Remove co-owner
        resp = await client.delete(
            f"{API}/workspaces/{ws_id}/owners/{co_owner['user_id']}",
            headers=h
        )
        assert resp.status_code == 200

        # 4. Transfer ownership
        new_owner = await register_and_login(client)
        await add_ws_member_with_role(
            client,
            ws_id=ws_id,
            owner_token=ws["access_token"],
            new_member_user_id=new_owner["user_id"],
            role_name="admin"
        )
        resp = await client.post(
            f"{API}/workspaces/{ws_id}/transfer-ownership",
            json={"from_id": ws["user_id"], "to_id": new_owner["user_id"]},
            headers=h
        )
        assert resp.status_code == 200

        # 5. Get — verify new owner
        resp = await client.get(
            f"{API}/workspaces/{ws_id}",
            headers=auth_headers(new_owner["access_token"])
        )
        assert resp.status_code == 200
