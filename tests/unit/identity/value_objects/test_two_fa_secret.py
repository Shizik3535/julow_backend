"""Unit-тесты для TwoFASecret."""

import pytest

from app.shared.domain.exceptions import ValidationException
from app.context.identity.domain.value_objects.two_fa_secret import TwoFASecret
from app.context.identity.domain.value_objects.two_factor_method import TwoFactorMethod


@pytest.mark.unit
class TestTwoFASecret:
    def test_valid_secret(self) -> None:
        secret = TwoFASecret(value="JBSWY3DPEHPK3PXP", method=TwoFactorMethod.TOTP)
        assert secret.value == "JBSWY3DPEHPK3PXP"
        assert secret.method == TwoFactorMethod.TOTP

    def test_empty_secret_raises(self) -> None:
        with pytest.raises(ValidationException):
            TwoFASecret(value="", method=TwoFactorMethod.TOTP)

    def test_whitespace_secret_raises(self) -> None:
        with pytest.raises(ValidationException):
            TwoFASecret(value="   ", method=TwoFactorMethod.TOTP)

    def test_equality(self) -> None:
        s1 = TwoFASecret(value="abc", method=TwoFactorMethod.TOTP)
        s2 = TwoFASecret(value="abc", method=TwoFactorMethod.TOTP)
        assert s1 == s2
