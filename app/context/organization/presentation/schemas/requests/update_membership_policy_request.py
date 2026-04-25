from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class UpdateMembershipPolicyRequest(BaseModel):
    """
    Тело запроса обновления политики членства.

    Атрибуты:
        allow_invitation_links: Разрешить ссылки-приглашения.
        default_role: Роль по умолчанию для новых участников.
        require_approval: Приглашения требуют подтверждения.
        max_members: Максимум участников.
        allowed_email_domains: Разрешённые домены email.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "allow_invitation_links": True,
                "default_role": "member",
                "require_approval": False,
                "max_members": 100,
                "allowed_email_domains": ["example.com"],
            },
        },
    )

    allow_invitation_links: bool = Field(default=True, description="Разрешить ссылки-приглашения")
    default_role: str = Field(default="member", max_length=100, description="Роль по умолчанию", examples=["member"])
    require_approval: bool = Field(default=False, description="Приглашения требуют подтверждения")
    max_members: int | None = Field(default=None, ge=1, description="Максимум участников", examples=[100])
    allowed_email_domains: list[str] = Field(default_factory=list, description="Разрешённые домены email")
