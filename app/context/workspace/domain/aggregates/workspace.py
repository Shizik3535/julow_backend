from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.shared.domain.base_aggregate import AggregateRoot
from app.shared.domain.value_objects.id_vo import Id
from app.shared.domain.value_objects.url_vo import Url
from app.context.workspace.domain.value_objects.workspace_status import WorkspaceStatus
from app.context.workspace.domain.value_objects.workspace_type import WorkspaceType
from app.context.workspace.domain.value_objects.workspace_personalization import WorkspacePersonalization
from app.context.workspace.domain.value_objects.workspace_branding import WorkspaceBranding
from app.context.workspace.domain.value_objects.security_policy import SecurityPolicy
from app.context.workspace.domain.value_objects.membership_policy import MembershipPolicy
from app.shared.domain.changed_fields import changed_fields
from app.context.workspace.domain.value_objects.workspace_limits import WorkspaceLimits
from app.context.workspace.domain.events.workspace_events import (
    WorkspaceCreated,
    WorkspaceInfoChanged,
    WorkspaceArchived,
    WorkspaceRestored,
    WorkspaceSuspended,
    WorkspaceReactivated,
    WorkspaceDeletionRequested,
    OwnershipTransferred,
    WorkspacePersonalizationChanged,
    SecurityPolicyChanged,
    MembershipPolicyChanged,
    WorkspaceLimitsChanged,
    ChildWorkspaceCreated,
)
from app.context.workspace.domain.exceptions.workspace_exceptions import (
    CannotRemoveLastOwnerException,
    CannotTransferOwnershipException,
    WorkspaceSuspendedException,
    WorkspaceArchivedException,
    CannotArchiveWithChildrenException,
    WorkspaceAlreadyArchivedException,
    WorkspaceNotArchivedException,
    WorkspaceAlreadySuspendedException,
    WorkspaceNotSuspendedException,
    WorkspaceDeletionAlreadyRequestedException,
    WorkspacePendingDeletionException,
)


@dataclass
class Workspace(AggregateRoot):
    """
    Корень агрегата workspace (Workspace BC).

    Ядро workspace — идентичность, статус, владельцы, политики, иерархия.
    Не содержит списки членов/команд (это отдельные AR).
    Связь через workspace_id (opaque ID).

    Атрибуты:
        name: Название workspace.
        status: Статус workspace.
        workspace_type: Тип workspace.
        organization_id: Opaque ID организации (None — независимый).
        parent_workspace_id: Opaque ID родительского workspace (None — корневой).
        personalization: Настройки персонализации.
        owner_ids: Список ID владельцев.
        security_policy: Политика безопасности.
        membership_policy: Политика членства.
        limits: Лимиты workspace.
        created_at: Время создания.
        updated_at: Время последнего обновления.
    """

    name: str = ""
    status: WorkspaceStatus = WorkspaceStatus.ACTIVE
    workspace_type: WorkspaceType = WorkspaceType.TEAM
    organization_id: Id | None = None
    parent_workspace_id: Id | None = None
    personalization: WorkspacePersonalization = field(default_factory=WorkspacePersonalization)
    owner_ids: list[Id] = field(default_factory=list)
    security_policy: SecurityPolicy = field(default_factory=SecurityPolicy)
    membership_policy: MembershipPolicy = field(default_factory=MembershipPolicy)
    limits: WorkspaceLimits = field(default_factory=WorkspaceLimits)
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))

    # --- Фабричный метод ---

    @classmethod
    def create(
        cls,
        name: str,
        owner_id: Id,
        workspace_type: WorkspaceType,
        organization_id: Id | None = None,
        parent_workspace_id: Id | None = None,
    ) -> Workspace:
        """Создаёт workspace с владельцем."""
        ws = cls(
            name=name,
            owner_ids=[owner_id],
            workspace_type=workspace_type,
            organization_id=organization_id,
            parent_workspace_id=parent_workspace_id,
        )
        ws._register_event(
            WorkspaceCreated(
                workspace_id=str(ws.id),
                owner_id=str(owner_id),
                name=name,
                organization_id=str(organization_id) if organization_id else "",
                parent_workspace_id=str(parent_workspace_id) if parent_workspace_id else "",
                workspace_type=workspace_type,
            )
        )
        if parent_workspace_id is not None:
            ws._register_event(
                ChildWorkspaceCreated(
                    parent_workspace_id=str(parent_workspace_id),
                    child_workspace_id=str(ws.id),
                )
            )
        return ws

    # --- Инварианты ---

    def _assert_can_modify(self) -> None:
        """Проверяет, что workspace допускает изменения."""
        if self.status == WorkspaceStatus.SUSPENDED:
            raise WorkspaceSuspendedException()
        if self.status == WorkspaceStatus.ARCHIVED:
            raise WorkspaceArchivedException()
        if self.status == WorkspaceStatus.PENDING_DELETION:
            raise WorkspacePendingDeletionException()

    def _assert_not_pending_deletion(self) -> None:
        """Проверяет, что workspace не в процессе удаления."""
        if self.status == WorkspaceStatus.PENDING_DELETION:
            raise WorkspacePendingDeletionException()

    # --- Информация ---

    def update_info(self, name: str | None = None, personalization: WorkspacePersonalization | None = None) -> None:
        """Обновляет информацию workspace."""
        self._assert_can_modify()
        changed: list[str] = []
        pers_changed: list[str] = []
        if name is not None and self.name != name:
            self.name = name
            changed.append("name")
        if personalization is not None:
            pers_changed = changed_fields(self.personalization, personalization)
            self.personalization = personalization
            changed.extend(f"personalization.{f}" for f in pers_changed)
        if changed:
            self.updated_at = datetime.now(tz=timezone.utc)
            self._register_event(
                WorkspaceInfoChanged(workspace_id=str(self.id), changed_fields=changed)
            )
            if pers_changed:
                self._register_event(
                    WorkspacePersonalizationChanged(workspace_id=str(self.id), changed_fields=pers_changed)
                )

    # --- Логотип ---

    def change_logo(self, logo_url: Url) -> None:
        """Обновляет URL логотипа workspace."""
        self._assert_can_modify()
        branding = self.personalization.branding or WorkspaceBranding()
        new_branding = WorkspaceBranding(
            logo_url=logo_url,
            cover_image_url=branding.cover_image_url,
            custom_css=branding.custom_css,
        )
        new_personalization = WorkspacePersonalization(
            color=self.personalization.color,
            icon=self.personalization.icon,
            display_name=self.personalization.display_name,
            description=self.personalization.description,
            branding=new_branding,
        )
        self.personalization = new_personalization
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            WorkspaceInfoChanged(workspace_id=str(self.id), changed_fields=["personalization.branding.logo_url"])
        )
        self._register_event(
            WorkspacePersonalizationChanged(workspace_id=str(self.id), changed_fields=["branding.logo_url"])
        )

    # --- Владельцы ---

    def add_owner(self, user_id: Id) -> None:
        """Добавляет со-владельца."""
        self._assert_can_modify()
        if user_id not in self.owner_ids:
            self.owner_ids.append(user_id)
            self.updated_at = datetime.now(tz=timezone.utc)

    def remove_owner(self, user_id: Id) -> None:
        """Удаляет владельца. Инвариант: минимум один владелец."""
        self._assert_can_modify()
        if len(self.owner_ids) <= 1:
            raise CannotRemoveLastOwnerException()
        if user_id in self.owner_ids:
            self.owner_ids.remove(user_id)
            self.updated_at = datetime.now(tz=timezone.utc)

    def transfer_ownership(self, from_id: Id, to_id: Id) -> None:
        """Передаёт владение от одного пользователя другому."""
        self._assert_can_modify()
        if from_id not in self.owner_ids:
            raise CannotTransferOwnershipException(reason="Передающий не является владельцем")
        if to_id in self.owner_ids:
            raise CannotTransferOwnershipException(reason="Получающий уже является владельцем")
        self.owner_ids.remove(from_id)
        self.owner_ids.append(to_id)
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            OwnershipTransferred(
                workspace_id=str(self.id),
                old_owner_id=str(from_id),
                new_owner_id=str(to_id),
            )
        )

    # --- Статус ---

    def archive(self) -> None:
        """Архивирует workspace. Нельзя архивировать с активными дочерними (проверка на app-слое)."""
        if self.status == WorkspaceStatus.ARCHIVED:
            raise WorkspaceAlreadyArchivedException()
        self._assert_can_modify()
        self.status = WorkspaceStatus.ARCHIVED
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            WorkspaceArchived(workspace_id=str(self.id))
        )

    def restore(self) -> None:
        """Восстанавливает workspace из архива."""
        if self.status != WorkspaceStatus.ARCHIVED:
            raise WorkspaceNotArchivedException()
        self.status = WorkspaceStatus.ACTIVE
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            WorkspaceRestored(workspace_id=str(self.id))
        )

    def suspend(self, reason: str) -> None:
        """Приостанавливает workspace."""
        self._assert_not_pending_deletion()
        if self.status == WorkspaceStatus.SUSPENDED:
            raise WorkspaceAlreadySuspendedException()
        self.status = WorkspaceStatus.SUSPENDED
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            WorkspaceSuspended(workspace_id=str(self.id), reason=reason)
        )

    def reactivate(self) -> None:
        """Реактивирует workspace."""
        if self.status != WorkspaceStatus.SUSPENDED:
            raise WorkspaceNotSuspendedException()
        self.status = WorkspaceStatus.ACTIVE
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            WorkspaceReactivated(workspace_id=str(self.id))
        )

    def request_deletion(self) -> None:
        """Запрашивает удаление workspace."""
        if self.status == WorkspaceStatus.PENDING_DELETION:
            raise WorkspaceDeletionAlreadyRequestedException()
        self._assert_can_modify()
        self.status = WorkspaceStatus.PENDING_DELETION
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            WorkspaceDeletionRequested(workspace_id=str(self.id))
        )

    # --- Политики ---

    def update_security_policy(self, policy: SecurityPolicy) -> None:
        """Обновляет политику безопасности."""
        self._assert_can_modify()
        changed = changed_fields(self.security_policy, policy)
        self.security_policy = policy
        self.updated_at = datetime.now(tz=timezone.utc)
        if changed:
            self._register_event(
                SecurityPolicyChanged(workspace_id=str(self.id), changed_fields=changed)
            )

    def update_membership_policy(self, policy: MembershipPolicy) -> None:
        """Обновляет политику членства."""
        self._assert_can_modify()
        changed = changed_fields(self.membership_policy, policy)
        self.membership_policy = policy
        self.updated_at = datetime.now(tz=timezone.utc)
        if changed:
            self._register_event(
                MembershipPolicyChanged(workspace_id=str(self.id), changed_fields=changed)
            )

    def update_limits(self, limits: WorkspaceLimits) -> None:
        """Обновляет лимиты workspace."""
        self._assert_can_modify()
        changed = changed_fields(self.limits, limits)
        self.limits = limits
        self.updated_at = datetime.now(tz=timezone.utc)
        if changed:
            self._register_event(
                WorkspaceLimitsChanged(workspace_id=str(self.id), changed_fields=changed)
            )

    # --- Иерархия ---

    def move_under_parent(self, parent_workspace_id: Id) -> None:
        """Перемещает workspace под родительский. Циклы проверяются на app-слое."""
        self._assert_can_modify()
        self.parent_workspace_id = parent_workspace_id
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            ChildWorkspaceCreated(
                parent_workspace_id=str(parent_workspace_id),
                child_workspace_id=str(self.id),
            )
        )

    def detach_from_parent(self) -> None:
        """Делает workspace корневым (отсоединяет от родителя)."""
        self._assert_can_modify()
        self.parent_workspace_id = None
        self.updated_at = datetime.now(tz=timezone.utc)
