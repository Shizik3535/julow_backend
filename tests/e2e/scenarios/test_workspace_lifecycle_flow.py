import pytest
from httpx import AsyncClient

from tests.e2e.conftest import (
    API,
    auth_headers
)


@pytest.mark.e2e
class TestWorkspaceLifecycleFlow:
    """Сценарий: полный lifecycle workspace — create → get → update → archive → restore → suspend → reactivate → request_deletion."""

    async def test_full_lifecycle(self, client: AsyncClient, workspace_lifecycle):
        ws = workspace_lifecycle
        h = auth_headers(ws["access_token"])
        ws_id = ws["ws_id"]

        # 1. Get
        resp = await client.get(f"{API}/workspaces/{ws_id}", headers=h)
        assert resp.status_code == 200
        assert resp.json()["data"]["name"] == "Lifecycle WS"

        # 2. Update info
        resp = await client.patch(
            f"{API}/workspaces/{ws_id}",
            json={"name": "Updated Lifecycle WS"},
            headers=h
        )
        assert resp.status_code == 200

        # 3. Archive
        resp = await client.post(f"{API}/workspaces/{ws_id}/archive", headers=h)
        assert resp.status_code == 200

        # 4. Restore
        resp = await client.post(f"{API}/workspaces/{ws_id}/restore", headers=h)
        assert resp.status_code == 200

        # 5. Suspend
        resp = await client.post(
            f"{API}/workspaces/{ws_id}/suspend",
            json={"reason": "Testing"},
            headers=h
        )
        assert resp.status_code == 200

        # 6. Reactivate
        resp = await client.post(f"{API}/workspaces/{ws_id}/reactivate", headers=h)
        assert resp.status_code == 200

        # 7. Request deletion
        resp = await client.post(f"{API}/workspaces/{ws_id}/request-deletion", headers=h)
        assert resp.status_code == 200
