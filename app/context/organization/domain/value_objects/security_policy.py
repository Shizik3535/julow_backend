from __future__ import annotations

from dataclasses import dataclass, field

from app.shared.domain.base_value_object import ValueObject
from app.shared.domain.exceptions import ValidationException


@dataclass(frozen=True)
class SecurityPolicy(ValueObject):
    """
    Политика безопасности организации.

    Атрибуты:
        require_2fa: Требовать двухфакторную аутентификацию.
        password_min_length: Минимальная длина пароля.
        session_timeout_minutes: Таймаут сессии в минутах (None — без ограничения).
        ip_allowlist: Список разрешённых IP-адресов.
        domain_restrictions: Ограничения доменов.
        require_email_verification: Требовать подтверждение email.
    """

    require_2fa: bool = False
    password_min_length: int = 8
    session_timeout_minutes: int | None = None
    ip_allowlist: list[str] = field(default_factory=list)
    domain_restrictions: list[str] = field(default_factory=list)
    require_email_verification: bool = False

    def __post_init__(self) -> None:
        if self.password_min_length < 8:
            raise ValidationException(
                field="password_min_length",
                message="Минимальная длина пароля должна быть не менее 8",
            )
        if self.session_timeout_minutes is not None and self.session_timeout_minutes < 1:
            raise ValidationException(
                field="session_timeout_minutes",
                message="Таймаут сессии должен быть не менее 1 минуты",
            )
