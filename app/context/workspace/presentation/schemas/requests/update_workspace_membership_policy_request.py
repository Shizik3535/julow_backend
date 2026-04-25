from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class UpdateWorkspaceMembershipPolicyRequest(BaseModel):
    """
    Запрос на обновление политики членства workspace.

    Атрибуты:
        allow_invitation_links: Разрешить ссылки-приглашения.
        default_role: Роль по умолчанию для новых участников.
        require_approval: Требуется ли подтверждение.
        max_members: Макс. количество участников.
        allowed_email_domains: Разрешённые email-домены.
        auto_add_from_org: Автодобавление из организации.
        inherit_from_parent: Наследовать от родителя.
    """

    model_config = ConfigDict(from_attributes=True)

    allow_invitation_links: bool | None = Field(default=None, description="Разрешить ссылки-приглашения")
    default_role: str | None = Field(default=None, description="Роль по умолчанию")
    require_approval: bool | None = Field(default=None, description="Требуется ли подтверждение")
    max_members: int | None = Field(default=None, description="Макс. количество участников")
    allowed_email_domains: list[str] | None = Field(default=None, description="Разрешённые email-домены")
    auto_add_from_org: bool | None = Field(default=None, description="Автодобавление из организации")
    inherit_from_parent: bool | None = Field(default=None, description="Наследовать от родителя")
