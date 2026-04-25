from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class UpdateWorkspaceSecurityPolicyRequest(BaseModel):
    """
    Запрос на обновление политики безопасности workspace.

    Атрибуты:
        pin_code_enabled: Включён ли PIN-код.
        password_enabled: Включён ли пароль.
        ip_allowlist: Список разрешённых IP/CIDR.
        sso_mode: Режим SSO (ONCE, EVERY_TIME, DISABLED).
        require_2fa: Требуется ли 2FA.
        session_timeout_minutes: Таймаут сессии (минуты).
        inherit_from_parent: Наследовать от родителя.
    """

    model_config = ConfigDict(from_attributes=True)

    pin_code_enabled: bool | None = Field(default=None, description="Включён ли PIN-код")
    password_enabled: bool | None = Field(default=None, description="Включён ли пароль")
    ip_allowlist: list[str] | None = Field(default=None, description="Список разрешённых IP/CIDR")
    sso_mode: str | None = Field(default=None, description="Режим SSO (ONCE, EVERY_TIME, DISABLED)")
    require_2fa: bool | None = Field(default=None, description="Требуется ли 2FA")
    session_timeout_minutes: int | None = Field(default=None, description="Таймаут сессии (минуты)")
    inherit_from_parent: bool | None = Field(default=None, description="Наследовать от родителя")
