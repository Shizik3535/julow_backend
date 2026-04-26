from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.shared.domain.base_aggregate import AggregateRoot
from app.shared.domain.value_objects.id_vo import Id
from app.context.project.domain.entities.project_member import ProjectMember
from app.context.project.domain.events.project_membership_events import (
    ProjectMemberJoined,
    ProjectMemberRemoved,
    ProjectMemberRoleChanged,
)
from app.context.project.domain.exceptions.project_membership_exceptions import (
    CannotRemoveOwnerAsMemberException,
    ProjectMemberNotFoundException,
)
from app.context.project.domain.value_objects.membership_type import MembershipType


@dataclass
class ProjectMembership(AggregateRoot):
    """
    Корень агрегата участников проекта (Project BC).

    Управление участниками проекта. Отдельный AR для масштабируемости.

    Атрибуты:
        project_id: Opaque ID проекта.
        members: Список участников.
        created_at: Время создания.
        updated_at: Время последнего обновления.
    """

    project_id: Id = field(default_factory=Id.generate)
    members: list[ProjectMember] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))

    @classmethod
    def create(cls, project_id: Id, owner_id: Id) -> ProjectMembership:
        """Создаёт членство проекта с владельцем."""
        membership = cls(project_id=project_id)
        owner_member = ProjectMember(user_id=owner_id)
        membership.members.append(owner_member)
        membership._register_event(
            ProjectMemberJoined(
                project_id=str(project_id),
                user_id=str(owner_id),
                role_id="",
            )
        )
        return membership

    def _find_member(self, user_id: Id) -> ProjectMember | None:
        return next((m for m in self.members if m.user_id == user_id), None)

    def _get_member(self, user_id: Id) -> ProjectMember:
        member = self._find_member(user_id)
        if member is None:
            raise ProjectMemberNotFoundException(id=user_id)
        return member

    def add_member(
        self,
        user_id: Id,
        role_id: Id,
        invited_by: Id | None = None,
        membership_type: MembershipType = MembershipType.STANDARD,
    ) -> None:
        """Добавляет участника в проект."""
        member = ProjectMember(user_id=user_id, role_id=role_id, membership_type=membership_type)
        self.members.append(member)
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            ProjectMemberJoined(
                project_id=str(self.project_id),
                user_id=str(user_id),
                role_id=str(role_id),
            )
        )

    def remove_member(self, user_id: Id, is_owner: bool = False) -> None:
        """Удаляет участника из проекта."""
        if is_owner:
            raise CannotRemoveOwnerAsMemberException(user_id=str(user_id))
        member = self._get_member(user_id)
        self.members.remove(member)
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            ProjectMemberRemoved(project_id=str(self.project_id), user_id=str(user_id))
        )

    def deactivate_member(self, user_id: Id, is_owner: bool = False) -> None:
        if is_owner:
            raise CannotRemoveOwnerAsMemberException(user_id=str(user_id))
        member = self._get_member(user_id)
        member.is_active = False
        self.updated_at = datetime.now(tz=timezone.utc)

    def reactivate_member(self, user_id: Id) -> None:
        member = self._get_member(user_id)
        member.is_active = True
        self.updated_at = datetime.now(tz=timezone.utc)

    def change_member_role(self, user_id: Id, new_role_id: Id) -> None:
        member = self._get_member(user_id)
        member.role_id = new_role_id
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            ProjectMemberRoleChanged(
                project_id=str(self.project_id),
                user_id=str(user_id),
                new_role_id=str(new_role_id),
            )
        )
