"""Интеграционные тесты OnSecurityPolicyCascade."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.application.event_handlers.on_security_policy_changed_cascade import (
    OnSecurityPolicyCascade,
)
from app.context.workspace.domain.value_objects.workspace_type import WorkspaceType


@pytest.mark.integration
class TestOnSecurityPolicyCascade:
    """Тесты OnSecurityPolicyCascade."""

    @pytest.fixture
    def handler(self, ws_repo) -> OnSecurityPolicyCascade:
        return OnSecurityPolicyCascade(ws_repo=ws_repo)

    async def test_cascade_to_inheriting_child(
        self, handler, ws_repo, make_workspace
    ) -> None:
        parent = await make_workspace(name="Sec Parent")
        child = await make_workspace(name="Sec Child", parent_workspace_id=parent.id)

        from app.context.workspace.domain.value_objects.security_policy import SecurityPolicy
        from app.context.workspace.domain.value_objects.sso_mode import SSOMode

        child_policy = SecurityPolicy(
            pin_code_enabled=False,
            password_enabled=True,
            ip_allowlist=[],
            sso_mode=SSOMode.NONE,
            require_2fa=False,
            session_timeout_minutes=None,
            inherit_from_parent=True,
        )
        child.update_security_policy(child_policy)
        child.clear_domain_events()
        await ws_repo.update(child)

        new_policy = SecurityPolicy(
            pin_code_enabled=True,
            password_enabled=True,
            ip_allowlist=["10.0.0.1"],
            sso_mode=SSOMode.OPTIONAL,
            require_2fa=True,
            session_timeout_minutes=60,
            inherit_from_parent=False,
        )
        parent.update_security_policy(new_policy)
        parent.clear_domain_events()
        await ws_repo.update(parent)

        event = {
            "event_type": "SecurityPolicyChanged",
            "payload": {"workspace_id": str(parent.id)},
        }
        await handler.handle(event)

        updated_child = await ws_repo.get_by_id(child.id)
        assert updated_child is not None
        assert updated_child.security_policy.pin_code_enabled is True
        assert updated_child.security_policy.require_2fa is True
        assert updated_child.security_policy.session_timeout_minutes == 60

    async def test_skip_non_inheriting_child(
        self, handler, ws_repo, make_workspace
    ) -> None:
        parent = await make_workspace(name="Sec Parent 2")
        child = await make_workspace(name="Sec Child 2", parent_workspace_id=parent.id)

        from app.context.workspace.domain.value_objects.security_policy import SecurityPolicy
        from app.context.workspace.domain.value_objects.sso_mode import SSOMode

        child_policy = SecurityPolicy(
            pin_code_enabled=False,
            password_enabled=True,
            ip_allowlist=[],
            sso_mode=SSOMode.NONE,
            require_2fa=False,
            session_timeout_minutes=None,
            inherit_from_parent=False,
        )
        child.update_security_policy(child_policy)
        child.clear_domain_events()
        await ws_repo.update(child)

        new_policy = SecurityPolicy(
            pin_code_enabled=True,
            password_enabled=True,
            ip_allowlist=[],
            sso_mode=SSOMode.NONE,
            require_2fa=True,
            session_timeout_minutes=30,
            inherit_from_parent=False,
        )
        parent.update_security_policy(new_policy)
        parent.clear_domain_events()
        await ws_repo.update(parent)

        event = {
            "event_type": "SecurityPolicyChanged",
            "payload": {"workspace_id": str(parent.id)},
        }
        await handler.handle(event)

        updated_child = await ws_repo.get_by_id(child.id)
        assert updated_child is not None
        assert updated_child.security_policy.pin_code_enabled is False

    async def test_ignore_non_target_event(self, handler) -> None:
        event = {"event_type": "OtherEvent", "payload": {}}
        await handler.handle(event)
