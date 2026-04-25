from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.shared.domain.base_aggregate import AggregateRoot
from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.domain.entities.org_member import OrgMember
from app.context.organization.domain.events.org_membership_events import (
    OrgMemberJoined,
    OrgMemberDisplayNameChanged,
    OrgMemberRoleChanged,
    OrgMemberRemoved,
    OrgMemberDeactivated,
    OrgMemberReactivated,
)
from app.context.organization.domain.exceptions.org_membership_exceptions import (
    CannotRemoveOwnerAsMemberException,
    OrgMemberAlreadyActiveException,
    OrgMemberAlreadyDeactivatedException,
    OrgMemberNotFoundException,
)


@dataclass
class OrgMembership(AggregateRoot):
    """
    Корень агрегата участников организации (Organization BC).

    Управление участниками организации. Отдельный AR для масштабируемости —
    тысячи членов не загружаются в Organization.
    Связь с Organization через org_id (opaque ID).

    Атрибуты:
        org_id: Opaque ID организации.
        members: Список участников.
        created_at: Время создания.
        updated_at: Время последнего обновления.
    """

    org_id: Id = field(default_factory=Id.generate)
    members: list[OrgMember] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))

    # --- Фабричный метод ---

    @classmethod
    def create(cls, org_id: Id, owner_id: Id, owner_role_id: Id) -> OrgMembership:
        """Создаёт членство организации с владельцем."""
        membership = cls(org_id=org_id)
        owner_member = OrgMember(user_id=owner_id, role_id=owner_role_id)
        membership.members.append(owner_member)
        membership._register_event(
            OrgMemberJoined(
                org_id=str(org_id),
                user_id=str(owner_id),
                role_id=str(owner_role_id),
            )
        )
        return membership

    # --- Поиск ---

    def _find_member(self, user_id: Id) -> OrgMember | None:
        """Находит участника по user_id."""
        return next((m for m in self.members if m.user_id == user_id), None)

    def _get_member(self, user_id: Id) -> OrgMember:
        """Находит участника или бросает исключение."""
        member = self._find_member(user_id)
        if member is None:
            raise OrgMemberNotFoundException(id=user_id)
        return member

    # --- Участники ---

    def add_member(
        self,
        user_id: Id,
        role_id: Id,
        invited_by: Id | None = None,
        display_name: str | None = None,
    ) -> None:
        """Добавляет участника в организацию."""
        member = OrgMember(
            user_id=user_id,
            role_id=role_id,
            invited_by=invited_by,
            display_name=display_name,
        )
        self.members.append(member)
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            OrgMemberJoined(
                org_id=str(self.org_id),
                user_id=str(user_id),
                role_id=str(role_id),
            )
        )

    def remove_member(self, user_id: Id, is_owner: bool = False) -> None:
        """Удаляет участника из организации."""
        if is_owner:
            raise CannotRemoveOwnerAsMemberException(user_id=str(user_id))
        member = self._get_member(user_id)
        self.members.remove(member)
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            OrgMemberRemoved(org_id=str(self.org_id), user_id=str(user_id))
        )

    def deactivate_member(self, user_id: Id, is_owner: bool = False) -> None:
        """Деактивирует участника."""
        if is_owner:
            raise CannotRemoveOwnerAsMemberException(user_id=str(user_id))
        member = self._get_member(user_id)
        if not member.is_active:
            raise OrgMemberAlreadyDeactivatedException(user_id=str(user_id))
        member.is_active = False
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            OrgMemberDeactivated(org_id=str(self.org_id), user_id=str(user_id))
        )

    def reactivate_member(self, user_id: Id) -> None:
        """Реактивирует участника."""
        member = self._get_member(user_id)
        if member.is_active:
            raise OrgMemberAlreadyActiveException(user_id=str(user_id))
        member.is_active = True
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            OrgMemberReactivated(org_id=str(self.org_id), user_id=str(user_id))
        )

    def change_member_role(self, user_id: Id, new_role_id: Id) -> None:
        """Изменяет роль участника."""
        member = self._get_member(user_id)
        member.role_id = new_role_id
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            OrgMemberRoleChanged(
                org_id=str(self.org_id),
                user_id=str(user_id),
                new_role_id=str(new_role_id),
            )
        )

    def update_member_display_name(self, user_id: Id, display_name: str) -> None:
        """Обновляет отображаемое имя участника."""
        member = self._get_member(user_id)
        member.display_name = display_name
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            OrgMemberDisplayNameChanged(
                org_id=str(self.org_id),
                user_id=str(user_id),
                display_name=display_name,
            )
        )
