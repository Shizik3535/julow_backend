from __future__ import annotations

from dataclasses import dataclass, field

from app.shared.domain.base_value_object import ValueObject
from app.shared.domain.exceptions import ValidationException


@dataclass(frozen=True)
class MembershipPolicy(ValueObject):
    """
    Политика членства в workspace.

    Атрибуты:
        allow_invitation_links: Разрешить ссылки-приглашения.
        default_role: Роль по умолчанию для новых участников.
        require_approval: Приглашения требуют подтверждения.
        max_members: Максимальное количество участников (None — без ограничения).
        allowed_email_domains: Разрешённые домены email для приглашений.
        auto_add_from_org: Автоматически добавлять участников из организации.
        inherit_from_parent: Наследовать политику от родительского workspace.
    """

    allow_invitation_links: bool = True
    default_role: str = "member"
    require_approval: bool = False
    max_members: int | None = None
    allowed_email_domains: list[str] = field(default_factory=list)
    auto_add_from_org: bool = False
    inherit_from_parent: bool = False

    def __post_init__(self) -> None:
        if not self.default_role:
            raise ValidationException(
                field="default_role",
                message="Роль по умолчанию не может быть пустой",
            )
        if self.max_members is not None and self.max_members < 1:
            raise ValidationException(
                field="max_members",
                message="Максимальное количество участников должно быть не менее 1",
            )
