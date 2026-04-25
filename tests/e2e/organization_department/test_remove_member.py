"""E2E-тесты: DELETE /orgs/{org_id}/departments/{department_id}/members/{user_id}."""

import uuid

import pytest

from tests.e2e.conftest import (
    API,
    add_member_to_org,
    auth_headers,
    create_org_with_owner,
    register_and_login,
)


@pytest.mark.e2e
class TestRemoveDepartmentMember:
    """Удаление участника из подразделения."""

    async def _setup_dept_with_member(self, client) -> dict:
        owner = await create_org_with_owner(client)
        resp = await client.post(
            f"{API}/orgs/{owner['org_id']}/departments",
            json={"name": "Dept With Member"},
            headers=auth_headers(owner["access_token"]),
        )
        dept_id = resp.json()["data"]["id"]
        member = await register_and_login(client)
        await add_member_to_org(
            client,
            org_id=owner["org_id"],
            owner_token=owner["access_token"],
            new_member_user_id=member["user_id"],
        )
        await client.post(
            f"{API}/orgs/{owner['org_id']}/departments/{dept_id}/members/{member['user_id']}",
            headers=auth_headers(owner["access_token"]),
        )
        return {**owner, "dept_id": dept_id, "member_id": member["user_id"]}

    async def test_remove_department_member_success(self, client) -> None:
        """200 — удаление участника из подразделения."""
        ctx = await self._setup_dept_with_member(client)
        resp = await client.delete(
            f"{API}/orgs/{ctx['org_id']}/departments/{ctx['dept_id']}/members/{ctx['member_id']}",
            headers=auth_headers(ctx["access_token"]),
        )

        assert resp.status_code == 200

    async def test_remove_department_member_forbidden(self, client) -> None:
        """403 — не-владелец не может удалить участника."""
        ctx = await self._setup_dept_with_member(client)
        other = await register_and_login(client)
        resp = await client.delete(
            f"{API}/orgs/{ctx['org_id']}/departments/{ctx['dept_id']}/members/{ctx['member_id']}",
            headers=auth_headers(other["access_token"]),
        )
        assert resp.status_code == 403

    async def test_remove_department_member_not_found(self, client) -> None:
        """404 — подразделение не найдено."""
        owner = await create_org_with_owner(client)
        resp = await client.delete(
            f"{API}/orgs/{owner['org_id']}/departments/{uuid.uuid4()}/members/{uuid.uuid4()}",
            headers=auth_headers(owner["access_token"]),
        )
        assert resp.status_code == 404

    async def test_remove_department_member_no_auth(self, client) -> None:
        """401 — без токена авторизации."""
        resp = await client.delete(
            f"{API}/orgs/{uuid.uuid4()}/departments/{uuid.uuid4()}/members/{uuid.uuid4()}",
        )
        assert resp.status_code == 401
