from __future__ import annotations

from dataclasses import dataclass, field

from app.shared.domain.base_value_object import ValueObject
from app.shared.domain.exceptions import ValidationException
from app.context.workspace.domain.value_objects.sso_mode import SSOMode


@dataclass(frozen=True)
class SecurityPolicy(ValueObject):
    """
    Политика безопасности workspace.

    Атрибуты:
        pin_code_enabled: Включён PIN-код.
        password_enabled: Включён пароль.
        ip_allowlist: Список разрешённых IP-адресов.
        sso_mode: Режим SSO.
        require_2fa: Требовать двухфакторную аутентификацию.
        session_timeout_minutes: Таймаут сессии в минутах (None — без ограничения).
        inherit_from_parent: Наследовать политику от родительского workspace.
    """

    pin_code_enabled: bool = False
    password_enabled: bool = True
    ip_allowlist: list[str] = field(default_factory=list)
    sso_mode: SSOMode = SSOMode.NONE
    require_2fa: bool = False
    session_timeout_minutes: int | None = None
    inherit_from_parent: bool = False

    def __post_init__(self) -> None:
        if self.session_timeout_minutes is not None and self.session_timeout_minutes < 1:
            raise ValidationException(
                field="session_timeout_minutes",
                message="Таймаут сессии должен быть не менее 1 минуты",
            )
