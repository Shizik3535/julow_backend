"""Unit-тесты check_overdue_projects — проверка публикации события ProjectOverdue."""

from datetime import date, timedelta
from unittest.mock import AsyncMock

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.project.domain.aggregates.project import Project
from app.context.project.domain.value_objects.methodology import Methodology
from app.context.project.domain.events.project_events import ProjectOverdue
from app.context.project.infrastructure.scheduling.check_overdue_projects import check_overdue_projects


class _StubCachePort:
    """In-memory stub для CachePort."""

    def __init__(self) -> None:
        self._store: dict[str, str] = {}

    async def get(self, key: str) -> str | None:
        return self._store.get(key)

    async def set(self, key: str, value: str, ttl: int | None = None) -> None:
        self._store[key] = value

    async def delete(self, key: str) -> None:
        self._store.pop(key, None)

    async def exists(self, key: str) -> bool:
        return key in self._store

    async def clear(self, pattern: str = "*") -> int:
        count = len(self._store)
        self._store.clear()
        return count


class _StubMember:
    """Stub для ProjectMembership member."""

    def __init__(self, user_id: Id, is_active: bool = True) -> None:
        self.user_id = user_id
        self.is_active = is_active


@pytest.mark.integration
class TestCheckOverdueProjects:
    """Тесты scheduled-задачи выявления просроченных проектов."""

    @pytest.fixture
    def project_repo(self) -> AsyncMock:
        repo = AsyncMock()
        repo.get_overdue_projects.return_value = []
        return repo

    @pytest.fixture
    def membership_repo(self) -> AsyncMock:
        repo = AsyncMock()
        repo.get_members_by_project.return_value = []
        return repo

    @pytest.fixture
    def cache_port(self) -> _StubCachePort:
        return _StubCachePort()

    @pytest.fixture
    def event_bus(self) -> AsyncMock:
        return AsyncMock()

    async def test_no_overdue_projects_no_events(
        self, project_repo, membership_repo, cache_port, event_bus
    ) -> None:
        project_repo.get_overdue_projects.return_value = []

        await check_overdue_projects(
            project_repo=project_repo,
            membership_repo=membership_repo,
            cache_port=cache_port,
            event_bus=event_bus,
        )

        event_bus.publish.assert_not_called()

    async def test_publishes_project_overdue_for_members_and_owners(
        self, project_repo, membership_repo, cache_port, event_bus
    ) -> None:
        owner_id = Id.generate()
        member_id = Id.generate()
        project = Project.create(
            name="Overdue Project",
            workspace_id=Id.generate(),
            owner_id=owner_id,
            methodology=Methodology.KANBAN,
        )
        project.update_info(deadline=date.today() - timedelta(days=1))
        project.clear_domain_events()

        project_repo.get_overdue_projects.return_value = [project]
        membership_repo.get_members_by_project.return_value = [
            _StubMember(user_id=member_id, is_active=True),
        ]

        await check_overdue_projects(
            project_repo=project_repo,
            membership_repo=membership_repo,
            cache_port=cache_port,
            event_bus=event_bus,
        )

        # owner + 1 member = 2 events
        assert event_bus.publish.call_count == 2
        for call in event_bus.publish.call_args_list:
            event = call.args[0]
            assert isinstance(event, ProjectOverdue)
            assert event.project_id == str(project.id)

    async def test_deduplication_skips_already_notified(
        self, project_repo, membership_repo, cache_port, event_bus
    ) -> None:
        owner_id = Id.generate()
        project = Project.create(
            name="Overdue Project",
            workspace_id=Id.generate(),
            owner_id=owner_id,
            methodology=Methodology.KANBAN,
        )
        project.update_info(deadline=date.today() - timedelta(days=1))
        project.clear_domain_events()

        project_repo.get_overdue_projects.return_value = [project]
        membership_repo.get_members_by_project.return_value = []

        # First run
        await check_overdue_projects(
            project_repo=project_repo,
            membership_repo=membership_repo,
            cache_port=cache_port,
            event_bus=event_bus,
        )
        assert event_bus.publish.call_count == 1

        # Second run — skips (dedup key exists)
        event_bus.publish.reset_mock()
        await check_overdue_projects(
            project_repo=project_repo,
            membership_repo=membership_repo,
            cache_port=cache_port,
            event_bus=event_bus,
        )
        event_bus.publish.assert_not_called()

    async def test_skips_project_without_deadline(
        self, project_repo, membership_repo, cache_port, event_bus
    ) -> None:
        owner_id = Id.generate()
        project = Project.create(
            name="No Deadline",
            workspace_id=Id.generate(),
            owner_id=owner_id,
            methodology=Methodology.KANBAN,
        )
        project.clear_domain_events()

        # deadline is None, but repo returned it anyway
        project_repo.get_overdue_projects.return_value = [project]

        await check_overdue_projects(
            project_repo=project_repo,
            membership_repo=membership_repo,
            cache_port=cache_port,
            event_bus=event_bus,
        )

        event_bus.publish.assert_not_called()

    async def test_excludes_inactive_members(
        self, project_repo, membership_repo, cache_port, event_bus
    ) -> None:
        owner_id = Id.generate()
        inactive_member = Id.generate()
        project = Project.create(
            name="Overdue Project",
            workspace_id=Id.generate(),
            owner_id=owner_id,
            methodology=Methodology.KANBAN,
        )
        project.update_info(deadline=date.today() - timedelta(days=1))
        project.clear_domain_events()

        project_repo.get_overdue_projects.return_value = [project]
        membership_repo.get_members_by_project.return_value = [
            _StubMember(user_id=inactive_member, is_active=False),
        ]

        await check_overdue_projects(
            project_repo=project_repo,
            membership_repo=membership_repo,
            cache_port=cache_port,
            event_bus=event_bus,
        )

        # Only owner gets notified (inactive member excluded)
        assert event_bus.publish.call_count == 1
