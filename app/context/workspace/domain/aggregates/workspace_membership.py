from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.shared.domain.base_aggregate import AggregateRoot
from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.domain.entities.workspace_member import WorkspaceMember
from app.context.workspace.domain.value_objects.member_source import MemberSource
from app.context.workspace.domain.events.workspace_membership_events import (
    WorkspaceMemberJoined,
    WorkspaceMemberDisplayNameChanged,
    WorkspaceMemberRoleChanged,
    WorkspaceMemberRemoved,
    WorkspaceMemberDeactivated,
    WorkspaceMemberReactivated,
    MemberAddedFromOrganization,
    MemberInheritedFromParent,
)
from app.context.workspace.domain.exceptions.workspace_membership_exceptions import (
    CannotRemoveOwnerAsMemberException,
    WorkspaceMemberNotFoundException,
)


@dataclass
class WorkspaceMembership(AggregateRoot):
    """
    Корень агрегата участников workspace (Workspace BC).

    Управление участниками workspace. Отдельный AR для масштабируемости.
    Связь с Workspace через workspace_id (opaque ID).

    Атрибуты:
        workspace_id: Opaque ID workspace.
        members: Список участников.
        created_at: Время создания.
        updated_at: Время последнего обновления.
    """

    workspace_id: Id = field(default_factory=Id.generate)
    members: list[WorkspaceMember] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))

    # --- Фабричный метод ---

    @classmethod
    def create(cls, workspace_id: Id, owner_id: Id) -> WorkspaceMembership:
        """Создаёт членство workspace с владельцем."""
        membership = cls(workspace_id=workspace_id)
        owner_member = WorkspaceMember(
            user_id=owner_id,
            source=MemberSource.DIRECT,
        )
        membership.members.append(owner_member)
        membership._register_event(
            WorkspaceMemberJoined(
                workspace_id=str(workspace_id),
                user_id=str(owner_id),
                role_id="",
                source=MemberSource.DIRECT.value,
            )
        )
        return membership

    # --- Поиск ---

    def _find_member(self, user_id: Id) -> WorkspaceMember | None:
        """Находит участника по user_id."""
        return next((m for m in self.members if m.user_id == user_id), None)

    def _get_member(self, user_id: Id) -> WorkspaceMember:
        """Находит участника или бросает исключение."""
        member = self._find_member(user_id)
        if member is None:
            raise WorkspaceMemberNotFoundException(id=user_id)
        return member

    # --- Участники ---

    def add_member(
        self,
        user_id: Id,
        role_id: Id,
        source: MemberSource = MemberSource.DIRECT,
        invited_by: Id | None = None,
        display_name: str | None = None,
    ) -> None:
        """Добавляет участника в workspace."""
        member = WorkspaceMember(
            user_id=user_id,
            role_id=role_id,
            source=source,
            invited_by=invited_by,
            display_name=display_name,
        )
        self.members.append(member)
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            WorkspaceMemberJoined(
                workspace_id=str(self.workspace_id),
                user_id=str(user_id),
                role_id=str(role_id),
                source=source.value,
            )
        )

    def add_member_from_org(self, user_id: Id, role_id: Id) -> None:
        """Добавляет участника из организации (ACL)."""
        member = WorkspaceMember(
            user_id=user_id,
            role_id=role_id,
            source=MemberSource.ORGANIZATION,
        )
        self.members.append(member)
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            MemberAddedFromOrganization(
                workspace_id=str(self.workspace_id),
                user_id=str(user_id),
            )
        )

    def inherit_member_from_parent(self, user_id: Id, role_id: Id, parent_workspace_id: Id) -> None:
        """Наследует участника из родительского workspace."""
        member = WorkspaceMember(
            user_id=user_id,
            role_id=role_id,
            source=MemberSource.PARENT_WORKSPACE,
        )
        self.members.append(member)
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            MemberInheritedFromParent(
                workspace_id=str(self.workspace_id),
                user_id=str(user_id),
                parent_workspace_id=str(parent_workspace_id),
            )
        )

    def remove_member(self, user_id: Id, is_owner: bool = False) -> None:
        """Удаляет участника из workspace."""
        if is_owner:
            raise CannotRemoveOwnerAsMemberException(user_id=str(user_id))
        member = self._get_member(user_id)
        self.members.remove(member)
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            WorkspaceMemberRemoved(workspace_id=str(self.workspace_id), user_id=str(user_id))
        )

    def deactivate_member(self, user_id: Id, is_owner: bool = False) -> None:
        """Деактивирует участника."""
        if is_owner:
            raise CannotRemoveOwnerAsMemberException(user_id=str(user_id))
        member = self._get_member(user_id)
        member.is_active = False
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            WorkspaceMemberDeactivated(workspace_id=str(self.workspace_id), user_id=str(user_id))
        )

    def reactivate_member(self, user_id: Id) -> None:
        """Реактивирует участника."""
        member = self._get_member(user_id)
        member.is_active = True
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            WorkspaceMemberReactivated(workspace_id=str(self.workspace_id), user_id=str(user_id))
        )

    def change_member_role(self, user_id: Id, new_role_id: Id) -> None:
        """Изменяет роль участника."""
        member = self._get_member(user_id)
        member.role_id = new_role_id
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            WorkspaceMemberRoleChanged(
                workspace_id=str(self.workspace_id),
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
            WorkspaceMemberDisplayNameChanged(
                workspace_id=str(self.workspace_id),
                user_id=str(user_id),
                display_name=display_name,
            )
        )
