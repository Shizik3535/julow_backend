"""Unit-тесты для MembershipPolicy (Workspace BC)."""

import pytest

from app.shared.domain.exceptions import ValidationException
from app.context.workspace.domain.value_objects.membership_policy import MembershipPolicy


@pytest.mark.unit
class TestMembershipPolicy:
    def test_defaults(self) -> None:
        policy = MembershipPolicy()
        assert policy.allow_invitation_links is True
        assert policy.default_role == "member"
        assert policy.require_approval is False
        assert policy.max_members is None
        assert policy.allowed_email_domains == []
        assert policy.auto_add_from_org is False
        assert policy.inherit_from_parent is False

    def test_custom_values(self) -> None:
        policy = MembershipPolicy(
            allow_invitation_links=False,
            default_role="admin",
            require_approval=True,
            max_members=50,
            allowed_email_domains=["example.com"],
            auto_add_from_org=True,
            inherit_from_parent=True,
        )
        assert policy.allow_invitation_links is False
        assert policy.default_role == "admin"
        assert policy.max_members == 50

    def test_empty_default_role_raises(self) -> None:
        with pytest.raises(ValidationException) as exc_info:
            MembershipPolicy(default_role="")
        assert exc_info.value.field == "default_role"

    def test_max_members_less_than_1_raises(self) -> None:
        with pytest.raises(ValidationException) as exc_info:
            MembershipPolicy(max_members=0)
        assert exc_info.value.field == "max_members"

    def test_frozen(self) -> None:
        policy = MembershipPolicy()
        with pytest.raises(AttributeError):
            policy.default_role = "admin"  # type: ignore[misc]

    def test_equality_by_value(self) -> None:
        assert MembershipPolicy() == MembershipPolicy()
