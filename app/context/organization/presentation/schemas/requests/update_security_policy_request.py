from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class UpdateSecurityPolicyRequest(BaseModel):
    """
    Тело запроса обновления политики безопасности.

    Атрибуты:
        require_2fa: Требовать двухфакторную аутентификацию.
        password_min_length: Минимальная длина пароля.
        session_timeout_minutes: Таймаут сессии в минутах.
        ip_allowlist: Список разрешённых IP.
        domain_restrictions: Ограничения доменов.
        require_email_verification: Требовать подтверждение email.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "require_2fa": True,
                "password_min_length": 12,
                "session_timeout_minutes": 60,
                "ip_allowlist": ["192.168.1.0/24"],
                "domain_restrictions": ["example.com"],
                "require_email_verification": True,
            },
        },
    )

    require_2fa: bool = Field(default=False, description="Требовать двухфакторную аутентификацию")
    password_min_length: int = Field(default=8, ge=6, le=128, description="Минимальная длина пароля", examples=[8])
    session_timeout_minutes: int | None = Field(default=None, ge=1, description="Таймаут сессии в минутах", examples=[60])
    ip_allowlist: list[str] = Field(default_factory=list, description="Список разрешённых IP")
    domain_restrictions: list[str] = Field(default_factory=list, description="Ограничения доменов")
    require_email_verification: bool = Field(default=False, description="Требовать подтверждение email")
