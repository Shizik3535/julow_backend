from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.shared.domain.base_aggregate import AggregateRoot
from app.shared.domain.value_objects.id_vo import Id
from app.shared.domain.value_objects.url_vo import Url
from app.context.workspace.domain.exceptions.workspace_team_exceptions import (
    TeamMemberAlreadyExistsException,
    WorkspaceTeamNotFoundException,
)
from app.context.workspace.domain.events.workspace_team_events import (
    WorkspaceTeamCreated,
    WorkspaceTeamUpdated,
    WorkspaceTeamDeleted,
    WorkspaceTeamMemberAdded,
    WorkspaceTeamMemberRemoved,
)


@dataclass
class WorkspaceTeam(AggregateRoot):
    """
    Корень агрегата команды workspace (Workspace BC).

    Команда — самостоятельный AR. Связан с workspace через workspace_id.

    Атрибуты:
        workspace_id: Opaque ID workspace.
        name: Название команды.
        description: Описание.
        lead_id: ID лидера команды.
        member_ids: Список ID участников.
        icon_url: URL иконки.
        is_active: Активна ли команда.
        created_at: Время создания.
        updated_at: Время последнего обновления.
    """

    workspace_id: Id = field(default_factory=Id.generate)
    name: str = ""
    description: str | None = None
    lead_id: Id | None = None
    member_ids: list[Id] = field(default_factory=list)
    icon_url: Url | None = None
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))

    # --- Фабричный метод ---

    @classmethod
    def create(cls, workspace_id: Id, name: str, lead_id: Id | None = None) -> WorkspaceTeam:
        """Создаёт команду workspace."""
        team = cls(workspace_id=workspace_id, name=name, lead_id=lead_id)
        if lead_id is not None:
            team.member_ids.append(lead_id)
        team._register_event(
            WorkspaceTeamCreated(workspace_id=str(workspace_id), team_id=str(team.id))
        )
        return team

    # --- Инварианты ---

    def _assert_active(self) -> None:
        """Проверяет, что команда активна."""
        if not self.is_active:
            raise ValueError("Неактивная команда не может принимать участников")

    # --- Обновление ---

    def update(
        self,
        name: str | None = None,
        description: str | None = None,
        lead_id: Id | None = None,
        icon_url: Url | None = None,
    ) -> None:
        """Обновляет информацию команды."""
        changed: list[str] = []
        if name is not None and self.name != name:
            self.name = name
            changed.append("name")
        if description is not None and self.description != description:
            self.description = description
            changed.append("description")
        if lead_id is not None and self.lead_id != lead_id:
            self.lead_id = lead_id
            changed.append("lead_id")
        if icon_url is not None and self.icon_url != icon_url:
            self.icon_url = icon_url
            changed.append("icon_url")
        if changed:
            self.updated_at = datetime.now(tz=timezone.utc)
            self._register_event(
                WorkspaceTeamUpdated(
                    workspace_id=str(self.workspace_id),
                    team_id=str(self.id),
                    changed_fields=changed,
                )
            )

    # --- Участники ---

    def add_member(self, user_id: Id) -> None:
        """Добавляет участника в команду. Участник должен быть членом workspace (проверка на app-слое)."""
        self._assert_active()
        if user_id in self.member_ids:
            raise TeamMemberAlreadyExistsException(user_id)
        self.member_ids.append(user_id)
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            WorkspaceTeamMemberAdded(
                workspace_id=str(self.workspace_id),
                team_id=str(self.id),
                user_id=str(user_id),
            )
        )

    def remove_member(self, user_id: Id) -> None:
        """Удаляет участника из команды."""
        if user_id in self.member_ids:
            self.member_ids.remove(user_id)
            self.updated_at = datetime.now(tz=timezone.utc)
            self._register_event(
                WorkspaceTeamMemberRemoved(
                    workspace_id=str(self.workspace_id),
                    team_id=str(self.id),
                    user_id=str(user_id),
                )
            )

    # --- Статус ---

    def deactivate(self) -> None:
        """Деактивирует команду."""
        self.is_active = False
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            WorkspaceTeamDeleted(workspace_id=str(self.workspace_id), team_id=str(self.id))
        )

    def reactivate(self) -> None:
        """Реактивирует команду."""
        self.is_active = True
        self.updated_at = datetime.now(tz=timezone.utc)
