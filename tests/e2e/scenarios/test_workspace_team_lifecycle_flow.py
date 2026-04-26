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
class TestWorkspaceTeamLifecycleFlow:
    """Сценарий: create_team → get_teams → add_team_member → update_team → deactivate → reactivate → remove_team_member."""

    async def test_full_team_lifecycle(self, client: AsyncClient):
        ws = await create_workspace_with_owner(client)
        h = auth_headers(ws["access_token"])
        ws_id = ws["ws_id"]

        # 1. Create team
        resp = await client.post(
            f"{API}/workspaces/{ws_id}/teams",
            json={"name": "Flow Team"},
            headers=h,
        )
        assert resp.status_code == 201
        team_id = resp.json()["data"]["id"]

        # 2. Get teams
        resp = await client.get(f"{API}/workspaces/{ws_id}/teams", headers=h)
        assert resp.status_code == 200
        items = resp.json()["items"]
        assert any(t["id"] == team_id for t in items)

        # 3. Add team member
        new_user = await register_user(client)
        await add_ws_member_with_role(
            client,
            ws_id=ws_id,
            owner_token=ws["access_token"],
            new_member_user_id=new_user["user_id"],
            role_name="member",
        )
        resp = await client.post(
            f"{API}/workspaces/{ws_id}/teams/{team_id}/members/{new_user['user_id']}",
            headers=h,
        )
        assert resp.status_code == 200

        # 4. Update team
        resp = await client.patch(
            f"{API}/workspaces/{ws_id}/teams/{team_id}",
            json={"name": "Updated Flow Team"},
            headers=h,
        )
        assert resp.status_code == 200

        # 5. Deactivate
        resp = await client.post(
            f"{API}/workspaces/{ws_id}/teams/{team_id}/deactivate",
            headers=h,
        )
        assert resp.status_code == 200

        # 6. Reactivate
        resp = await client.post(
            f"{API}/workspaces/{ws_id}/teams/{team_id}/reactivate",
            headers=h,
        )
        assert resp.status_code == 200

        # 7. Remove team member
        resp = await client.delete(
            f"{API}/workspaces/{ws_id}/teams/{team_id}/members/{new_user['user_id']}",
            headers=h,
        )
        assert resp.status_code == 200
