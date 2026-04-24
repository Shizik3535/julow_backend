"""Unit-тесты для AuthFactor."""

import pytest

from app.context.identity.domain.entities.auth_factor import AuthFactor
from app.context.identity.domain.value_objects.two_factor_method import TwoFactorMethod
from app.context.identity.domain.value_objects.two_fa_secret import TwoFASecret


@pytest.mark.unit
class TestAuthFactor:
    def test_create_auth_factor(self) -> None:
        factor = AuthFactor(method=TwoFactorMethod.TOTP)
        assert factor.method == TwoFactorMethod.TOTP
        assert not factor.is_enabled
        assert not factor.is_primary

    def test_enable_factor(self) -> None:
        factor = AuthFactor(method=TwoFactorMethod.TOTP)
        secret = TwoFASecret(value="JBSWY3DPEHPK3PXP", method=TwoFactorMethod.TOTP)
        factor.enable(secret, is_primary=True)
        assert factor.is_enabled
        assert factor.is_primary
        assert factor.verified_at is not None

    def test_disable_factor(self) -> None:
        factor = AuthFactor(method=TwoFactorMethod.TOTP)
        secret = TwoFASecret(value="JBSWY3DPEHPK3PXP", method=TwoFactorMethod.TOTP)
        factor.enable(secret)
        factor.disable()
        assert not factor.is_enabled
        assert not factor.is_primary
