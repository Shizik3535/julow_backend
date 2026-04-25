from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.shared.domain.base_aggregate import AggregateRoot
from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.domain.exceptions.department_exceptions import DepartmentMemberAlreadyExistsException
from app.context.organization.domain.events.department_events import (
    DepartmentCreated,
    DepartmentUpdated,
    DepartmentDeleted,
    DepartmentMemberAdded,
    DepartmentMemberRemoved,
)


@dataclass
class Department(AggregateRoot):
    """
    Корень агрегата подразделения (Organization BC).

    Связан с организацией через org_id. Поддерживает иерархию через parent_id.

    Атрибуты:
        org_id: Opaque ID организации.
        name: Название подразделения.
        parent_id: Opaque ID родительского подразделения (None — корневое).
        lead_id: ID руководителя.
        member_ids: Список ID участников.
        is_active: Активно ли подразделение.
        created_at: Время создания.
        updated_at: Время последнего обновления.
    """

    org_id: Id = field(default_factory=Id.generate)
    name: str = ""
    parent_id: Id | None = None
    lead_id: Id | None = None
    member_ids: list[Id] = field(default_factory=list)
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))

    # --- Фабричный метод ---

    @classmethod
    def create(
        cls,
        org_id: Id,
        name: str,
        parent_id: Id | None = None,
        lead_id: Id | None = None,
    ) -> Department:
        """Создаёт подразделение."""
        department = cls(org_id=org_id, name=name, parent_id=parent_id, lead_id=lead_id)
        department._register_event(
            DepartmentCreated(org_id=str(org_id), department_id=str(department.id))
        )
        return department

    # --- Обновление ---

    def update(self, name: str | None = None, lead_id: Id | None = None) -> None:
        """Обновляет подразделение."""
        changed: list[str] = []
        if name is not None and self.name != name:
            self.name = name
            changed.append("name")
        if lead_id is not None and self.lead_id != lead_id:
            self.lead_id = lead_id
            changed.append("lead_id")
        if changed:
            self.updated_at = datetime.now(tz=timezone.utc)
            self._register_event(
                DepartmentUpdated(
                    org_id=str(self.org_id),
                    department_id=str(self.id),
                    changed_fields=changed,
                )
            )

    # --- Участники ---

    def add_member(self, user_id: Id) -> None:
        """Добавляет участника в подразделение."""
        if user_id in self.member_ids:
            raise DepartmentMemberAlreadyExistsException(
                user_id=str(user_id), department_id=str(self.id)
            )
        self.member_ids.append(user_id)
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            DepartmentMemberAdded(
                org_id=str(self.org_id),
                department_id=str(self.id),
                user_id=str(user_id),
            )
        )

    def remove_member(self, user_id: Id) -> None:
        """Удаляет участника из подразделения."""
        if user_id in self.member_ids:
            self.member_ids.remove(user_id)
            self.updated_at = datetime.now(tz=timezone.utc)
            self._register_event(
                DepartmentMemberRemoved(
                    org_id=str(self.org_id),
                    department_id=str(self.id),
                    user_id=str(user_id),
                )
            )

    # --- Статус ---

    def deactivate(self) -> None:
        """Деактивирует подразделение."""
        self.is_active = False
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            DepartmentDeleted(org_id=str(self.org_id), department_id=str(self.id))
        )

    def reactivate(self) -> None:
        """Реактивирует подразделение."""
        self.is_active = True
        self.updated_at = datetime.now(tz=timezone.utc)
