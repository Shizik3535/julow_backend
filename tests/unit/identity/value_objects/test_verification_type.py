"""Unit-тесты для VerificationType."""

import pytest

from app.context.identity.domain.value_objects.verification_type import VerificationType


@pytest.mark.unit
class TestVerificationType:
    def test_all_types_exist(self) -> None:
        assert VerificationType.EMAIL_CONFIRMATION.value == "email_confirmation"
        assert VerificationType.PASSWORD_RESET.value == "password_reset"
        assert VerificationType.ACCOUNT_DELETION.value == "account_deletion"
        assert VerificationType.EMAIL_CHANGE.value == "email_change"
