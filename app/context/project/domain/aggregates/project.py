from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timezone

from app.shared.domain.base_aggregate import AggregateRoot
from app.shared.domain.value_objects.id_vo import Id
from app.shared.domain.value_objects.color_vo import Color
from app.shared.domain.value_objects.rich_text_vo import RichText
from app.context.project.domain.value_objects.project_status import ProjectStatus
from app.context.project.domain.value_objects.project_visibility import ProjectVisibility
from app.context.project.domain.value_objects.methodology import Methodology
from app.context.project.domain.value_objects.methodology_capabilities import MethodologyCapabilities
from app.context.project.domain.value_objects.category import Category
from app.shared.domain.changed_fields import changed_fields
from app.context.project.domain.value_objects.custom_field_definition import CustomFieldDefinition
from app.context.project.domain.entities.milestone import Milestone
from app.context.project.domain.value_objects.milestone_status import MilestoneStatus
from app.context.project.domain.events.project_events import (
    ProjectCreated,
    ProjectInfoChanged,
    ProjectArchived,
    ProjectRestored,
    ProjectSuspended,
    ProjectReactivated,
    ProjectDeletionRequested,
    MethodologyChanged,
    ProjectVisibilityChanged,
    MilestoneCreated,
    MilestoneUpdated,
    MilestoneStatusChanged,
)
from app.context.project.domain.exceptions.project_exceptions import (
    CannotChangeMethodologyWithActiveSprintsException,
    CannotTransferOwnershipException,
    MilestoneNotFoundException,
    ProjectSuspendedException,
    ProjectArchivedException,
    ProjectPendingDeletionException,
)
from app.context.project.domain.exceptions.project_membership_exceptions import (
    CannotRemoveLastOwnerException,
)
from app.context.project.domain.exceptions.custom_field_exceptions import (
    DuplicateCustomFieldException,
    CustomFieldDefinitionNotFoundException,
)


@dataclass
class Project(AggregateRoot):
    """
    Корень агрегата проекта (Project BC).

    Ядро проекта — идентичность, статус, методология, владельцы, политики.
    Не содержит доски/спринты (это отдельные AR).
    Связь через project_id (opaque ID).

    Атрибуты:
        workspace_id: Opaque ID workspace (из Workspace BC).
        name: Название проекта.
        description: Описание (форматированный текст).
        icon: Иконка.
        color: Акцентный цвет (из shared kernel).
        category: Категория.
        methodology: Методология.
        methodology_capabilities: Возможности методологии.
        visibility: Видимость проекта.
        status: Статус проекта.
        owner_ids: Список ID владельцев.
        start_date: Дата начала.
        deadline: Дедлайн.
        milestones: Список milestones (entities).
        custom_field_definitions: Список кастомных полей (VOs).
        created_at: Время создания.
        updated_at: Время последнего обновления.
    """

    workspace_id: Id | None = None
    name: str = ""
    description: RichText | None = None
    icon: str | None = None
    color: Color | None = None
    category: Category | None = None
    methodology: Methodology = Methodology.KANBAN
    methodology_capabilities: MethodologyCapabilities = field(default_factory=MethodologyCapabilities)
    visibility: ProjectVisibility = ProjectVisibility.PRIVATE
    status: ProjectStatus = ProjectStatus.ACTIVE
    owner_ids: list[Id] = field(default_factory=list)
    start_date: date | None = None
    deadline: date | None = None
    milestones: list[Milestone] = field(default_factory=list)
    custom_field_definitions: list[CustomFieldDefinition] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))

    # --- Фабричный метод ---

    @classmethod
    def create(
        cls,
        name: str,
        workspace_id: Id,
        owner_id: Id,
        methodology: Methodology,
    ) -> Project:
        """Создаёт проект с владельцем и методологией."""
        capabilities = MethodologyCapabilities.for_methodology(methodology)
        project = cls(
            name=name,
            workspace_id=workspace_id,
            owner_ids=[owner_id],
            methodology=methodology,
            methodology_capabilities=capabilities,
        )
        project._register_event(
            ProjectCreated(
                project_id=str(project.id),
                workspace_id=str(workspace_id),
                name=name,
                methodology=methodology,
            )
        )
        return project

    # --- Инварианты ---

    def _assert_can_modify(self) -> None:
        if self.status == ProjectStatus.SUSPENDED:
            raise ProjectSuspendedException()
        if self.status == ProjectStatus.ARCHIVED:
            raise ProjectArchivedException()
        if self.status == ProjectStatus.PENDING_DELETION:
            raise ProjectPendingDeletionException()

    def _assert_not_pending_deletion(self) -> None:
        if self.status == ProjectStatus.PENDING_DELETION:
            raise ProjectPendingDeletionException()

    # --- Информация ---

    def update_info(
        self,
        name: str | None = None,
        description: RichText | None = None,
        icon: str | None = None,
        color: Color | None = None,
        category: Category | None = None,
        start_date: date | None = None,
        deadline: date | None = None,
    ) -> None:
        """Обновляет информацию проекта."""
        self._assert_can_modify()
        changed: list[str] = []
        if name is not None and self.name != name:
            self.name = name
            changed.append("name")
        if description is not None and self.description != description:
            self.description = description
            changed.append("description")
        if icon is not None and self.icon != icon:
            self.icon = icon
            changed.append("icon")
        if color is not None and self.color != color:
            self.color = color
            changed.append("color")
        if category is not None and self.category != category:
            self.category = category
            changed.append("category")
        if start_date is not None and self.start_date != start_date:
            self.start_date = start_date
            changed.append("start_date")
        if deadline is not None and self.deadline != deadline:
            self.deadline = deadline
            changed.append("deadline")
        if changed:
            self.updated_at = datetime.now(tz=timezone.utc)
            self._register_event(
                ProjectInfoChanged(project_id=str(self.id), changed_fields=changed)
            )

    # --- Владельцы ---

    def add_owner(self, user_id: Id) -> None:
        self._assert_can_modify()
        if user_id not in self.owner_ids:
            self.owner_ids.append(user_id)
            self.updated_at = datetime.now(tz=timezone.utc)

    def remove_owner(self, user_id: Id) -> None:
        self._assert_can_modify()
        if len(self.owner_ids) <= 1:
            raise CannotRemoveLastOwnerException()
        if user_id in self.owner_ids:
            self.owner_ids.remove(user_id)
            self.updated_at = datetime.now(tz=timezone.utc)

    def transfer_ownership(self, from_id: Id, to_id: Id) -> None:
        self._assert_can_modify()
        if from_id not in self.owner_ids:
            raise CannotTransferOwnershipException(reason="Передающий не является владельцем")
        if to_id in self.owner_ids:
            raise CannotTransferOwnershipException(reason="Получающий уже является владельцем")
        self.owner_ids.remove(from_id)
        self.owner_ids.append(to_id)
        self.updated_at = datetime.now(tz=timezone.utc)

    # --- Статус ---

    def archive(self) -> None:
        self._assert_can_modify()
        self.status = ProjectStatus.ARCHIVED
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(ProjectArchived(project_id=str(self.id)))

    def restore(self) -> None:
        if self.status != ProjectStatus.ARCHIVED:
            return
        self.status = ProjectStatus.ACTIVE
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(ProjectRestored(project_id=str(self.id)))

    def suspend(self, reason: str) -> None:
        self._assert_not_pending_deletion()
        if self.status == ProjectStatus.SUSPENDED:
            return
        self.status = ProjectStatus.SUSPENDED
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(ProjectSuspended(project_id=str(self.id), reason=reason))

    def reactivate(self) -> None:
        if self.status != ProjectStatus.SUSPENDED:
            return
        self.status = ProjectStatus.ACTIVE
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(ProjectReactivated(project_id=str(self.id)))

    def request_deletion(self) -> None:
        self._assert_can_modify()
        self.status = ProjectStatus.PENDING_DELETION
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(ProjectDeletionRequested(project_id=str(self.id)))

    # --- Методология ---

    def change_methodology(self, new_methodology: Methodology, has_active_sprints: bool = False) -> None:
        """Сменяет методологию. Проверка активных спринтов — на app-слое."""
        self._assert_can_modify()
        if has_active_sprints:
            raise CannotChangeMethodologyWithActiveSprintsException()
        old = self.methodology
        self.methodology = new_methodology
        self.methodology_capabilities = MethodologyCapabilities.for_methodology(new_methodology)
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            MethodologyChanged(
                project_id=str(self.id),
                old_methodology=old,
                new_methodology=new_methodology,
            )
        )

    # --- Видимость ---

    def change_visibility(self, visibility: ProjectVisibility) -> None:
        self._assert_can_modify()
        self.visibility = visibility
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            ProjectVisibilityChanged(project_id=str(self.id), new_visibility=visibility)
        )

    # --- Кастомные поля ---

    def add_custom_field(self, definition: CustomFieldDefinition) -> None:
        self._assert_can_modify()
        if any(f.name == definition.name for f in self.custom_field_definitions):
            raise DuplicateCustomFieldException(name=definition.name)
        self.custom_field_definitions.append(definition)
        self.updated_at = datetime.now(tz=timezone.utc)

    def update_custom_field(self, name: str, definition: CustomFieldDefinition) -> None:
        self._assert_can_modify()
        for i, f in enumerate(self.custom_field_definitions):
            if f.name == name:
                self.custom_field_definitions[i] = definition
                self.updated_at = datetime.now(tz=timezone.utc)
                return
        raise CustomFieldDefinitionNotFoundException(name=name)

    def remove_custom_field(self, name: str) -> None:
        self._assert_can_modify()
        for i, f in enumerate(self.custom_field_definitions):
            if f.name == name:
                self.custom_field_definitions.pop(i)
                self.updated_at = datetime.now(tz=timezone.utc)
                return
        raise CustomFieldDefinitionNotFoundException(name=name)

    # --- Milestones ---

    def add_milestone(self, milestone: Milestone) -> None:
        self._assert_can_modify()
        self.milestones.append(milestone)
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            MilestoneCreated(project_id=str(self.id), milestone_id=str(milestone.id))
        )

    def update_milestone(
        self,
        milestone_id: Id,
        name: str | None = None,
        description: RichText | None = None,
        due_date: date | None = None,
    ) -> None:
        self._assert_can_modify()
        milestone = next((m for m in self.milestones if m.id == milestone_id), None)
        if milestone is None:
            raise MilestoneNotFoundException(milestone_id)
        changed: list[str] = []
        if name is not None and milestone.name != name:
            milestone.name = name
            changed.append("name")
        if description is not None and milestone.description != description:
            milestone.description = description
            changed.append("description")
        if due_date is not None and milestone.due_date != due_date:
            milestone.due_date = due_date
            changed.append("due_date")
        if changed:
            self.updated_at = datetime.now(tz=timezone.utc)
            self._register_event(
                MilestoneUpdated(
                    project_id=str(self.id),
                    milestone_id=str(milestone_id),
                    changed_fields=changed,
                )
            )

    def change_milestone_status(self, milestone_id: Id, new_status: MilestoneStatus) -> None:
        self._assert_can_modify()
        milestone = next((m for m in self.milestones if m.id == milestone_id), None)
        if milestone is None:
            raise MilestoneNotFoundException(milestone_id)
        milestone.status = new_status
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            MilestoneStatusChanged(
                project_id=str(self.id),
                milestone_id=str(milestone_id),
                new_status=new_status,
            )
        )
