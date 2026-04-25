from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.shared.domain.base_aggregate import AggregateRoot
from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.domain.value_objects.org_status import OrgStatus
from app.context.organization.domain.value_objects.org_personalization import OrgPersonalization
from app.context.organization.domain.value_objects.security_policy import SecurityPolicy
from app.context.organization.domain.value_objects.membership_policy import MembershipPolicy
from app.context.organization.domain.events.organization_events import (
    OrganizationCreated,
    OrganizationInfoChanged,
    OrganizationSuspended,
    OrganizationReactivated,
    OrganizationDeletionRequested,
    OwnershipTransferred,
    OrgPersonalizationChanged,
    SecurityPolicyChanged,
    MembershipPolicyChanged,
)
from app.context.organization.domain.exceptions.organization_exceptions import (
    CannotRemoveLastOwnerException,
    CannotTransferOwnershipException,
    OrganizationAlreadyActiveException,
    OrganizationAlreadySuspendedException,
    OrganizationDeletionAlreadyRequestedException,
    OrganizationSuspendedException,
)


def _changed_fields(old_vo: object, new_vo: object) -> list[str]:
    """Вычисляет список имён изменённых полей между двумя VO-группами."""
    changed: list[str] = []
    for f_name in type(old_vo).__dataclass_fields__:
        if getattr(old_vo, f_name) != getattr(new_vo, f_name):
            changed.append(f_name)
    return changed


@dataclass
class Organization(AggregateRoot):
    """
    Корень агрегата организации (Organization BC).

    Ядро организации — идентичность, статус, владельцы, политики.
    Не содержит списки членов/команд (это отдельные AR).
    Связь через org_id (opaque ID).

    Атрибуты:
        name: Название организации.
        status: Статус организации.
        personalization: Настройки персонализации.
        owner_ids: Список ID владельцев.
        security_policy: Политика безопасности.
        membership_policy: Политика членства.
        created_at: Время создания.
        updated_at: Время последнего обновления.
    """

    name: str = ""
    status: OrgStatus = OrgStatus.ACTIVE
    personalization: OrgPersonalization = field(default_factory=OrgPersonalization)
    owner_ids: list[Id] = field(default_factory=list)
    security_policy: SecurityPolicy = field(default_factory=SecurityPolicy)
    membership_policy: MembershipPolicy = field(default_factory=MembershipPolicy)
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))

    # --- Фабричный метод ---

    @classmethod
    def create(cls, name: str, owner_id: Id) -> Organization:
        """Создаёт организацию с владельцем."""
        org = cls(name=name, owner_ids=[owner_id])
        org._register_event(
            OrganizationCreated(
                org_id=str(org.id),
                owner_id=str(owner_id),
                name=name,
            )
        )
        return org

    # --- Инварианты ---

    def _assert_not_suspended(self) -> None:
        """Проверяет, что организация не приостановлена."""
        if self.status == OrgStatus.SUSPENDED:
            raise OrganizationSuspendedException()

    def _assert_not_pending_deletion(self) -> None:
        """Проверяет, что организация не в процессе удаления."""
        if self.status == OrgStatus.PENDING_DELETION:
            raise OrganizationSuspendedException()

    def _assert_can_modify(self) -> None:
        """Проверяет, что организация допускает изменения."""
        self._assert_not_suspended()
        self._assert_not_pending_deletion()

    # --- Информация ---

    def update_info(self, name: str | None = None, personalization: OrgPersonalization | None = None) -> None:
        """Обновляет информацию организации."""
        self._assert_can_modify()
        changed: list[str] = []
        if name is not None and self.name != name:
            self.name = name
            changed.append("name")
        pers_changed: list[str] = []
        if personalization is not None:
            pers_changed = _changed_fields(self.personalization, personalization)
            self.personalization = personalization
            changed.extend(f"personalization.{f}" for f in pers_changed)
        if changed:
            self.updated_at = datetime.now(tz=timezone.utc)
            self._register_event(
                OrganizationInfoChanged(org_id=str(self.id), changed_fields=changed)
            )
            if pers_changed:
                self._register_event(
                    OrgPersonalizationChanged(org_id=str(self.id), changed_fields=pers_changed)
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
                org_id=str(self.id),
                old_owner_id=str(from_id),
                new_owner_id=str(to_id),
            )
        )

    # --- Статус ---

    def suspend(self, reason: str) -> None:
        """Приостанавливает организацию."""
        self._assert_not_pending_deletion()
        if self.status == OrgStatus.SUSPENDED:
            raise OrganizationAlreadySuspendedException()
        self.status = OrgStatus.SUSPENDED
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            OrganizationSuspended(org_id=str(self.id), reason=reason)
        )

    def reactivate(self) -> None:
        """Реактивирует организацию."""
        if self.status != OrgStatus.SUSPENDED:
            raise OrganizationAlreadyActiveException()
        self.status = OrgStatus.ACTIVE
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            OrganizationReactivated(org_id=str(self.id))
        )

    def request_deletion(self) -> None:
        """Запрашивает удаление организации."""
        if self.status == OrgStatus.PENDING_DELETION:
            raise OrganizationDeletionAlreadyRequestedException()
        self._assert_can_modify()
        self.status = OrgStatus.PENDING_DELETION
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            OrganizationDeletionRequested(org_id=str(self.id))
        )

    # --- Политики ---

    def update_security_policy(self, policy: SecurityPolicy) -> None:
        """Обновляет политику безопасности."""
        self._assert_can_modify()
        changed = _changed_fields(self.security_policy, policy)
        self.security_policy = policy
        self.updated_at = datetime.now(tz=timezone.utc)
        if changed:
            self._register_event(
                SecurityPolicyChanged(org_id=str(self.id), changed_fields=changed)
            )

    def update_membership_policy(self, policy: MembershipPolicy) -> None:
        """Обновляет политику членства."""
        self._assert_can_modify()
        changed = _changed_fields(self.membership_policy, policy)
        self.membership_policy = policy
        self.updated_at = datetime.now(tz=timezone.utc)
        if changed:
            self._register_event(
                MembershipPolicyChanged(org_id=str(self.id), changed_fields=changed)
            )
