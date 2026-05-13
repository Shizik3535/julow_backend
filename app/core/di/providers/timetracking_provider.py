"""DI-провайдеры для TimeTracking BC."""
from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.context.identity.application.ports.integration.outboard.identity_user_provider import (
    IdentityUserProvider,
)
from app.context.project.application.ports.integration.outboard.epic_provider import EpicProvider
from app.context.project.application.ports.integration.outboard.project_provider import (
    ProjectProvider,
)
from app.context.task.application.ports.integration.outboard.task_provider import TaskProvider
from app.context.timetracking.application.ports.authorization.timetracking_permission_checker_port import (
    TimeTrackingPermissionCheckerPort,
)
from app.context.timetracking.application.ports.integration.inboard.epic_port import EpicPort
from app.context.timetracking.application.ports.integration.inboard.identity_user_port import (
    IdentityUserPort,
)
from app.context.timetracking.application.ports.integration.inboard.project_port import (
    ProjectPort,
)
from app.context.timetracking.application.ports.integration.inboard.task_port import TaskPort
from app.context.timetracking.application.ports.integration.inboard.workspace_port import (
    WorkspacePort,
)
from app.context.timetracking.domain.repositories.activity_category_repository import (
    ActivityCategoryRepository,
)
from app.context.timetracking.domain.repositories.time_entry_repository import (
    TimeEntryRepository,
)
from app.context.timetracking.domain.repositories.time_entry_tag_repository import (
    TimeEntryTagRepository,
)
from app.context.timetracking.infrastructure.authorization.timetracking_role_based_permission_checker import (
    TimeTrackingRoleBasedPermissionChecker,
)
from app.context.timetracking.infrastructure.integration.inboard.epic_adapter import EpicAdapter
from app.context.timetracking.infrastructure.integration.inboard.identity_user_adapter import (
    IdentityUserAdapter,
)
from app.context.timetracking.infrastructure.integration.inboard.project_adapter import (
    ProjectAdapter,
)
from app.context.timetracking.infrastructure.integration.inboard.task_adapter import TaskAdapter
from app.context.timetracking.infrastructure.integration.inboard.workspace_adapter import (
    WorkspaceAdapter,
)
from app.context.timetracking.infrastructure.persistence.mappers.activity_category_mapper import (
    ActivityCategoryMapper,
)
from app.context.timetracking.infrastructure.persistence.mappers.time_entry_mapper import (
    TimeEntryMapper,
)
from app.context.timetracking.infrastructure.persistence.mappers.time_entry_tag_mapper import (
    TimeEntryTagMapper,
)
from app.context.timetracking.infrastructure.persistence.repositories.sql_activity_category_repository import (
    SqlActivityCategoryRepository,
)
from app.context.timetracking.infrastructure.persistence.repositories.sql_time_entry_repository import (
    SqlTimeEntryRepository,
)
from app.context.timetracking.infrastructure.persistence.repositories.sql_time_entry_tag_repository import (
    SqlTimeEntryTagRepository,
)
from app.context.workspace.application.ports.integration.outboard.workspace_membership_provider import (
    WorkspaceMembershipProvider,
)
from app.context.workspace.application.ports.integration.outboard.workspace_provider import (
    WorkspaceProvider,
)


# --- Mappers ---

def create_time_entry_mapper() -> TimeEntryMapper:
    return TimeEntryMapper()


def create_activity_category_mapper() -> ActivityCategoryMapper:
    return ActivityCategoryMapper()


def create_time_entry_tag_mapper() -> TimeEntryTagMapper:
    return TimeEntryTagMapper()


# --- Repositories ---

def create_time_entry_repository(
    session: AsyncSession, mapper: TimeEntryMapper
) -> TimeEntryRepository:
    return SqlTimeEntryRepository(session=session, mapper=mapper)


def create_activity_category_repository(
    session: AsyncSession, mapper: ActivityCategoryMapper
) -> ActivityCategoryRepository:
    return SqlActivityCategoryRepository(session=session, mapper=mapper)


def create_time_entry_tag_repository(
    session: AsyncSession, mapper: TimeEntryTagMapper
) -> TimeEntryTagRepository:
    return SqlTimeEntryTagRepository(session=session, mapper=mapper)


# --- Authorization ---

def create_timetracking_permission_checker(
    workspace_membership_provider: WorkspaceMembershipProvider,
) -> TimeTrackingPermissionCheckerPort:
    return TimeTrackingRoleBasedPermissionChecker(
        workspace_membership_provider=workspace_membership_provider,
    )


# --- Inboard adapters ---

def create_timetracking_workspace_adapter(
    workspace_provider: WorkspaceProvider,
    workspace_membership_provider: WorkspaceMembershipProvider,
) -> WorkspacePort:
    return WorkspaceAdapter(
        workspace_provider=workspace_provider,
        workspace_membership_provider=workspace_membership_provider,
    )


def create_timetracking_task_adapter(task_provider: TaskProvider) -> TaskPort:
    return TaskAdapter(task_provider=task_provider)


def create_timetracking_project_adapter(project_provider: ProjectProvider) -> ProjectPort:
    return ProjectAdapter(project_provider=project_provider)


def create_timetracking_epic_adapter(epic_provider: EpicProvider) -> EpicPort:
    return EpicAdapter(epic_provider=epic_provider)


def create_timetracking_identity_user_adapter(
    identity_user_provider: IdentityUserProvider,
) -> IdentityUserPort:
    return IdentityUserAdapter(identity_user_provider=identity_user_provider)
