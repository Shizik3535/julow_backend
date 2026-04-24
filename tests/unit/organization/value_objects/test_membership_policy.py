"""Unit-тесты для MembershipPolicy (Organization BC)."""

import pytest

from app.shared.domain.exceptions import ValidationException
from app.context.organization.domain.value_objects.membership_policy import MembershipPolicy


@pytest.mark.unit
class TestMembershipPolicy:
    def test_defaults(self) -> None:
        policy = MembershipPolicy()
        assert policy.allow_invitation_links is True
        assert policy.default_role == "member"
        assert policy.require_approval is False
        assert policy.max_members is None
        assert policy.allowed_email_domains == []

    def test_custom_values(self) -> None:
        policy = MembershipPolicy(
            allow_invitation_links=False,
            default_role="viewer",
            require_approval=True,
            max_members=50,
            allowed_email_domains=["example.com"],
        )
        assert policy.allow_invitation_links is False
        assert policy.default_role == "viewer"
        assert policy.require_approval is True
        assert policy.max_members == 50
        assert policy.allowed_email_domains == ["example.com"]

    def test_empty_default_role_raises(self) -> None:
        with pytest.raises(ValidationException) as exc_info:
            MembershipPolicy(default_role="")
        assert exc_info.value.field == "default_role"

    def test_max_members_less_than_one_raises(self) -> None:
        with pytest.raises(ValidationException) as exc_info:
            MembershipPolicy(max_members=0)
        assert exc_info.value.field == "max_members"

    def test_frozen(self) -> None:
        policy = MembershipPolicy()
        with pytest.raises(AttributeError):
            policy.default_role = "admin"  # type: ignore[misc]

    def test_equality_by_value(self) -> None:
        assert MembershipPolicy() == MembershipPolicy()
