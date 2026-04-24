from __future__ import annotations

import pyotp

from app.context.identity.application.ports.two_fa.totp_port import TOTPPort


class PyOTPTotpAdapter(TOTPPort):
    """
    Реализация TOTPPort на основе PyOTP.

    Генерирует TOTP-секреты, provisioning URI и верифицирует коды.
    """

    def generate_secret(self) -> str:
        return pyotp.random_base32()

    def get_provisioning_uri(self, secret: str, email: str, issuer: str) -> str:
        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(name=email, issuer_name=issuer)

    def verify_code(self, secret: str, code: str) -> bool:
        totp = pyotp.TOTP(secret)
        return totp.verify(code)
