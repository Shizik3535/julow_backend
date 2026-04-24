"""Unit-тесты для InvitationToken (Workspace BC)."""

from datetime import datetime, timedelta, timezone

import pytest

from app.shared.domain.exceptions import ValidationException
from app.context.workspace.domain.value_objects.invitation_token import InvitationToken


@pytest.mark.unit
class TestInvitationToken:
    def test_valid_token(self) -> None:
        token = InvitationToken(value="abc123")
        assert token.value == "abc123"
        assert token.expires_at is None
        assert token.max_uses is None
        assert token.used_count == 0

    def test_empty_value_raises(self) -> None:
        with pytest.raises(ValidationException) as exc_info:
            InvitationToken(value="")
        assert exc_info.value.field == "invitation_token"

    def test_max_uses_less_than_1_raises(self) -> None:
        with pytest.raises(ValidationException) as exc_info:
            InvitationToken(value="abc", max_uses=0)
        assert exc_info.value.field == "invitation_token"

    def test_used_count_negative_raises(self) -> None:
        with pytest.raises(ValidationException) as exc_info:
            InvitationToken(value="abc", used_count=-1)
        assert exc_info.value.field == "invitation_token"

    def test_is_expired_false_when_no_expiry(self) -> None:
        token = InvitationToken(value="abc")
        assert not token.is_expired

    def test_is_expired_false_when_future(self) -> None:
        future = datetime.now(tz=timezone.utc) + timedelta(hours=1)
        token = InvitationToken(value="abc", expires_at=future)
        assert not token.is_expired

    def test_is_expired_true_when_past(self) -> None:
        past = datetime.now(tz=timezone.utc) - timedelta(hours=1)
        token = InvitationToken(value="abc", expires_at=past)
        assert token.is_expired

    def test_is_max_uses_exceeded_false_when_no_limit(self) -> None:
        token = InvitationToken(value="abc", used_count=5)
        assert not token.is_max_uses_exceeded

    def test_is_max_uses_exceeded_false_when_under_limit(self) -> None:
        token = InvitationToken(value="abc", max_uses=5, used_count=3)
        assert not token.is_max_uses_exceeded

    def test_is_max_uses_exceeded_true(self) -> None:
        token = InvitationToken(value="abc", max_uses=3, used_count=3)
        assert token.is_max_uses_exceeded

    def test_frozen(self) -> None:
        token = InvitationToken(value="abc")
        with pytest.raises(AttributeError):
            token.value = "changed"  # type: ignore[misc]

    def test_equality_by_value(self) -> None:
        t1 = InvitationToken(value="abc", used_count=0)
        t2 = InvitationToken(value="abc", used_count=0)
        assert t1 == t2
