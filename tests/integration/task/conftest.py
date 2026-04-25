"""
Task BC conftest — фикстуры для integration-тестов Task.

Предоставляет mappers, repositories, seed-хелперы и стабы портов.
"""

import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.domain.value_objects.email_vo import Email
from app.shared.domain.value_objects.id_vo import Id
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.context.task.application.ports.authorization.task_permission_checker_port import (
    TaskPermissionCheckerPort,
)
from app.context.task.application.ports.integration.inboard.project_port import ProjectPort
from app.context.task.application.ports.integration.inboard.board_port import BoardPort
from app.context.task.application.ports.integration.inboard.sprint_port import SprintPort
from app.context.task.application.ports.integration.inboard.epic_port import EpicPort
from app.context.task.application.ports.integration.inboard.identity_user_port import IdentityUserPort
from app.context.task.application.ports.integration.inboard.project_membership_port import ProjectMembershipPort
from app.shared.application.ports.file_storage.file_storage_port import FileStoragePort
from app.shared.application.ports.file_storage.file_storage_dto import FileInfo

from app.context.identity.domain.aggregates.user import User
from app.context.identity.infrastructure.persistence.mappers.user_mapper import UserMapper
from app.context.identity.infrastructure.persistence.repositories.sql_user_repository import SqlUserRepository

from app.context.project.domain.aggregates.project import Project
from app.context.project.domain.value_objects.methodology import Methodology
from app.context.project.infrastructure.persistence.mappers.project_mapper import ProjectMapper
from app.context.project.infrastructure.persistence.repositories.sql_project_repository import SqlProjectRepository

from app.context.task.domain.aggregates.task import Task
from app.context.task.domain.aggregates.task_template import TaskTemplate
from app.context.task.domain.aggregates.changelog import ChangelogEntry
from app.context.task.domain.value_objects.task_type import TaskType
from app.context.task.domain.value_objects.task_priority import TaskPriority
from app.context.task.domain.value_objects.label import Label

from app.context.task.infrastructure.persistence.mappers.task_mapper import TaskMapper
from app.context.task.infrastructure.persistence.mappers.task_template_mapper import TaskTemplateMapper
from app.context.task.infrastructure.persistence.mappers.changelog_mapper import ChangelogMapper

from app.context.task.infrastructure.persistence.repositories.sql_task_repository import SqlTaskRepository
from app.context.task.infrastructure.persistence.repositories.sql_task_template_repository import (
    SqlTaskTemplateRepository,
)
from app.context.task.infrastructure.persistence.repositories.sql_changelog_repository import SqlChangelogRepository


# ── Identity Mappers & Repos (FK-зависимость) ──────────────────────────────


@pytest.fixture
def user_mapper() -> UserMapper:
    return UserMapper()


@pytest.fixture
def user_repo(db_session: AsyncSession, user_mapper: UserMapper) -> SqlUserRepository:
    return SqlUserRepository(session=db_session, mapper=user_mapper)


# ── Project Mapper & Repo (FK-зависимость) ──────────────────────────────────


@pytest.fixture
def project_mapper() -> ProjectMapper:
    return ProjectMapper()


@pytest.fixture
def project_repo(db_session: AsyncSession, project_mapper: ProjectMapper) -> SqlProjectRepository:
    return SqlProjectRepository(session=db_session, mapper=project_mapper)


# ── Task Mappers ────────────────────────────────────────────────────────────


@pytest.fixture
def task_mapper() -> TaskMapper:
    return TaskMapper()


@pytest.fixture
def task_template_mapper() -> TaskTemplateMapper:
    return TaskTemplateMapper()


@pytest.fixture
def changelog_mapper() -> ChangelogMapper:
    return ChangelogMapper()


# ── Task Repositories ──────────────────────────────────────────────────────


@pytest.fixture
def task_repo(db_session: AsyncSession, task_mapper: TaskMapper) -> SqlTaskRepository:
    return SqlTaskRepository(session=db_session, mapper=task_mapper)


@pytest.fixture
def task_template_repo(
    db_session: AsyncSession, task_template_mapper: TaskTemplateMapper
) -> SqlTaskTemplateRepository:
    return SqlTaskTemplateRepository(session=db_session, mapper=task_template_mapper)


@pytest.fixture
def changelog_repo(db_session: AsyncSession, changelog_mapper: ChangelogMapper) -> SqlChangelogRepository:
    return SqlChangelogRepository(session=db_session, mapper=changelog_mapper)


# ── Seed Helpers ──────────────────────────────────────────────────────────


@pytest.fixture
def _ensure_user(user_repo: SqlUserRepository):
    """Хелпер: гарантирует наличие User в БД для FK-зависимостей."""
    _created: set[Id] = set()

    async def _fn(user_id: Id | None = None) -> User:
        uid = user_id or Id.generate()
        found = await user_repo.get_by_id(uid)
        if found is not None:
            _created.add(uid)
            return found
        email_vo = Email(f"auto-task-{uuid.uuid4().hex[:8]}@test.com")
        user = User(id=uid, email=email_vo)
        user.clear_domain_events()
        await user_repo.add(user)
        _created.add(uid)
        return user

    return _fn


@pytest.fixture
def _ensure_project(project_repo: SqlProjectRepository, _ensure_user):
    """Хелпер: гарантирует наличие Project в БД для FK-зависимостей."""
    _created: set[Id] = set()

    async def _fn(project_id: Id | None = None) -> Project:
        pid = project_id or Id.generate()
        found = await project_repo.get_by_id(pid)
        if found is not None:
            _created.add(pid)
            return found
        owner_id = Id.generate()
        await _ensure_user(owner_id)
        ws_id = Id.generate()
        proj_name = f"auto-proj-{uuid.uuid4().hex[:6]}"
        project = Project.create(
            name=proj_name,
            workspace_id=ws_id,
            owner_id=owner_id,
            methodology=Methodology.KANBAN,
        )
        project.clear_domain_events()
        await project_repo.add(project)
        _created.add(pid)
        return project

    return _fn


@pytest.fixture
def make_user(user_repo: SqlUserRepository, _ensure_user):
    """Фабрика: создаёт User и сохраняет в БД."""

    async def _make(
        email: str | None = None,
    ) -> User:
        email_vo = Email(email or f"task-user-{uuid.uuid4().hex[:8]}@test.com")
        user = User(id=Id.generate(), email=email_vo)
        user.clear_domain_events()
        await user_repo.add(user)
        return user

    return _make


@pytest.fixture
def make_project(project_repo: SqlProjectRepository, _ensure_user):
    """Фабрика: создаёт Project с владельцем и сохраняет в БД."""

    async def _make(
        name: str | None = None,
        owner_id: Id | None = None,
        workspace_id: Id | None = None,
        methodology: Methodology = Methodology.KANBAN,
    ) -> Project:
        oid = owner_id or Id.generate()
        await _ensure_user(oid)
        ws_id = workspace_id or Id.generate()
        proj_name = name or f"task-proj-{uuid.uuid4().hex[:6]}"
        project = Project.create(
            name=proj_name,
            workspace_id=ws_id,
            owner_id=oid,
            methodology=methodology,
        )
        project.clear_domain_events()
        await project_repo.add(project)
        return project

    return _make


@pytest.fixture
def make_task(task_repo: SqlTaskRepository, _ensure_project):
    """Фабрика: создаёт Task и сохраняет в БД."""

    async def _make(
        title: str | None = None,
        project_id: Id | None = None,
        task_type: TaskType = TaskType.TASK,
        reporter_id: Id | None = None,
        parent_task_id: Id | None = None,
        epic_id: Id | None = None,
    ) -> Task:
        pid = project_id or Id.generate()
        await _ensure_project(pid)
        rid = reporter_id or Id.generate()
        task_title = title or f"task-{uuid.uuid4().hex[:6]}"
        task = Task.create(
            title=task_title,
            project_id=pid,
            task_type=task_type,
            reporter_id=rid,
            parent_task_id=parent_task_id,
            epic_id=epic_id,
        )
        task.clear_domain_events()
        await task_repo.add(task)
        return task

    return _make


@pytest.fixture
def make_task_template(task_template_repo: SqlTaskTemplateRepository):
    """Фабрика: создаёт TaskTemplate и сохраняет в БД."""

    async def _make(
        name: str | None = None,
        task_type: TaskType = TaskType.TASK,
        default_labels: list[Label] | None = None,
        is_system: bool = False,
        project_id: Id | None = None,
    ) -> TaskTemplate:
        tmpl_name = name or f"template-{uuid.uuid4().hex[:6]}"
        if is_system:
            template = TaskTemplate.create_system(
                name=tmpl_name,
                task_type=task_type,
                default_labels=default_labels or [],
            )
        else:
            template = TaskTemplate.create_custom(
                name=tmpl_name,
                task_type=task_type,
                project_id=project_id,
                default_labels=default_labels or [],
            )
        template.clear_domain_events()
        await task_template_repo.add(template)
        return template

    return _make


@pytest.fixture
def make_changelog_entry(changelog_repo: SqlChangelogRepository, make_task):
    """Фабрика: создаёт ChangelogEntry и сохраняет в БД."""

    async def _make(
        task_id: Id | None = None,
        field_name: str = "status_id",
        old_value: str | None = None,
        new_value: str | None = None,
        changed_by: Id | None = None,
    ) -> ChangelogEntry:
        if task_id is None:
            task = await make_task()
            task_id = task.id
        cb = changed_by or Id.generate()
        entry = ChangelogEntry.create(
            task_id=task_id,
            field_name=field_name,
            old_value=old_value,
            new_value=new_value,
            changed_by=cb,
        )
        entry.clear_domain_events()
        await changelog_repo.add(entry)
        return entry

    return _make


# ── Stubs for Command/Query/EventHandler Tests ──────────────────────────────


class _AlwaysAllowTaskPermissionChecker(TaskPermissionCheckerPort):
    """Stub: всегда разрешает любые действия с задачами."""

    async def has_permission(self, user_id: str, project_id: str, permission: str) -> bool:
        return True

    async def require_permission(self, user_id: str, project_id: str, permission: str) -> None:
        pass


class _AlwaysDenyTaskPermissionChecker(TaskPermissionCheckerPort):
    """Stub: всегда запрещает любые действия с задачами."""

    async def has_permission(self, user_id: str, project_id: str, permission: str) -> bool:
        return False

    async def require_permission(self, user_id: str, project_id: str, permission: str) -> None:
        from app.context.task.application.exceptions.authorization_exceptions import (
            InsufficientTaskPermissionsException,
        )
        raise InsufficientTaskPermissionsException(
            permission=permission, project_id=project_id, user_id=user_id
        )


class _StubProjectPort(ProjectPort):
    """Stub: считает, что все проекты существуют и активны."""

    def __init__(self, default_status_id: str | None = None) -> None:
        self._default_status_id = default_status_id

    async def project_exists(self, project_id: str) -> bool:
        return True

    async def get_project(self, project_id: str) -> dict | None:
        return {"id": project_id, "name": "Stub Project", "status": "active"}

    async def is_project_active(self, project_id: str) -> bool:
        return True


class _StubBoardPort(BoardPort):
    """Stub: возвращает фиксированный default_status_id, разрешает любой переход."""

    def __init__(self, default_status_id: str | None = None) -> None:
        self._default_status_id = default_status_id

    async def get_workflow_statuses(self, project_id: str) -> list[dict]:
        return []

    async def get_default_status_id(self, project_id: str) -> str | None:
        return self._default_status_id

    async def is_transition_allowed(
        self, project_id: str, from_status_id: str, to_status_id: str
    ) -> bool:
        return True

    async def get_columns(self, project_id: str) -> list[dict]:
        return []


class _StubSprintPort(SprintPort):
    """Stub: считает, что все спринты существуют."""

    async def sprint_exists(self, sprint_id: str) -> bool:
        return True

    async def get_sprint(self, sprint_id: str) -> dict | None:
        return {"id": sprint_id, "name": "Stub Sprint", "status": "ACTIVE"}

    async def get_active_sprint(self, project_id: str) -> dict | None:
        return None


class _StubEpicPort(EpicPort):
    """Stub: считает, что все эпики существуют."""

    async def epic_exists(self, epic_id: str) -> bool:
        return True

    async def get_epic(self, epic_id: str) -> dict | None:
        return {"id": epic_id, "name": "Stub Epic", "status": "active"}


class _StubIdentityUserPort(IdentityUserPort):
    """Stub: считает, что все пользователи существуют."""

    async def user_exists(self, user_id: str) -> bool:
        return True


class _StubProjectMembershipPort(ProjectMembershipPort):
    """Stub: считает, что все пользователи являются участниками проекта."""

    async def is_project_member(self, project_id: str, user_id: str) -> bool:
        return True


class _NoopEventBus(DomainEventBus):
    """Stub: поглощает все события без публикации."""

    async def publish_all(self, events: list) -> None:
        pass

    async def publish(self, event) -> None:
        pass


@pytest.fixture
def permission_checker_stub() -> _AlwaysAllowTaskPermissionChecker:
    return _AlwaysAllowTaskPermissionChecker()


@pytest.fixture
def permission_denied_stub() -> _AlwaysDenyTaskPermissionChecker:
    return _AlwaysDenyTaskPermissionChecker()


@pytest.fixture
def project_stub() -> _StubProjectPort:
    return _StubProjectPort()


@pytest.fixture
def board_stub() -> _StubBoardPort:
    return _StubBoardPort(default_status_id=str(Id.generate()))


@pytest.fixture
def sprint_stub() -> _StubSprintPort:
    return _StubSprintPort()


@pytest.fixture
def epic_stub() -> _StubEpicPort:
    return _StubEpicPort()


@pytest.fixture
def identity_user_stub() -> _StubIdentityUserPort:
    return _StubIdentityUserPort()


@pytest.fixture
def project_membership_stub() -> _StubProjectMembershipPort:
    return _StubProjectMembershipPort()


class _StubFileStorage(FileStoragePort):
    """Stub: имитирует загрузку файлов, не сохраняет данные."""

    async def upload(self, key: str, data: bytes, content_type: str = "application/octet-stream") -> FileInfo:
        return FileInfo(key=key, size=len(data), content_type=content_type)

    async def download(self, key: str) -> bytes:
        return b""

    async def delete(self, key: str) -> None:
        pass

    async def get_info(self, key: str) -> FileInfo | None:
        return None

    async def get_url(self, key: str, expires_in: int | None = 3600) -> str:
        return f"http://localhost/storage/{key}"


@pytest.fixture
def event_bus_stub() -> _NoopEventBus:
    return _NoopEventBus()


@pytest.fixture
def file_storage_stub() -> _StubFileStorage:
    return _StubFileStorage()
