"""Интеграционные тесты SqlProjectMembershipRepository (реальная PostgreSQL)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.project.domain.aggregates.project_membership import ProjectMembership
from app.context.project.infrastructure.persistence.repositories.sql_project_membership_repository import (
    SqlProjectMembershipRepository,
)


@pytest.mark.integration
class TestSqlProjectMembershipRepositoryAdd:
    """Тесты добавления."""

    async def test_add_and_get_by_id(self, membership_repo: SqlProjectMembershipRepository, make_project) -> None:
        proj = await make_project()
        owner_id = proj.owner_ids[0] if proj.owner_ids else Id.generate()
        membership = ProjectMembership.create(project_id=proj.id, owner_id=owner_id)
        membership.clear_domain_events()
        await membership_repo.add(membership)

        found = await membership_repo.get_by_id(membership.id)
        assert found is not None
        assert found.id == membership.id

    async def test_add_and_get_by_project_id(self, membership_repo: SqlProjectMembershipRepository, make_project) -> None:
        proj = await make_project()
        owner_id = proj.owner_ids[0] if proj.owner_ids else Id.generate()
        membership = ProjectMembership.create(project_id=proj.id, owner_id=owner_id)
        membership.clear_domain_events()
        await membership_repo.add(membership)

        found = await membership_repo.get_by_project_id(proj.id)
        assert found is not None
        assert found.project_id == proj.id


@pytest.mark.integration
class TestSqlProjectMembershipRepositorySearch:
    """Тесты поиска."""

    async def test_get_member_by_project_and_user(self, membership_repo: SqlProjectMembershipRepository, make_project) -> None:
        proj = await make_project()
        owner_id = proj.owner_ids[0] if proj.owner_ids else Id.generate()
        membership = ProjectMembership.create(project_id=proj.id, owner_id=owner_id)
        membership.clear_domain_events()
        await membership_repo.add(membership)

        member = await membership_repo.get_member_by_project_and_user(proj.id, owner_id)
        assert member is not None
        assert member.user_id == owner_id

    async def test_get_member_not_found(self, membership_repo: SqlProjectMembershipRepository, make_project) -> None:
        proj = await make_project()
        member = await membership_repo.get_member_by_project_and_user(proj.id, Id.generate())
        assert member is None

    async def test_get_members_by_project(self, membership_repo: SqlProjectMembershipRepository, make_project) -> None:
        proj = await make_project()
        owner_id = proj.owner_ids[0] if proj.owner_ids else Id.generate()
        membership = ProjectMembership.create(project_id=proj.id, owner_id=owner_id)
        membership.clear_domain_events()
        await membership_repo.add(membership)

        members = await membership_repo.get_members_by_project(proj.id)
        assert len(members) >= 1


@pytest.mark.integration
class TestSqlProjectMembershipRepositoryUpdate:
    """Тесты обновления."""

    async def test_update_add_member(self, membership_repo: SqlProjectMembershipRepository, make_project, make_user) -> None:
        proj = await make_project()
        owner_id = proj.owner_ids[0] if proj.owner_ids else Id.generate()
        membership = ProjectMembership.create(project_id=proj.id, owner_id=owner_id)
        membership.clear_domain_events()
        await membership_repo.add(membership)

        new_user = await make_user()
        membership.add_member(user_id=new_user.id, role_id=Id.generate())
        membership.clear_domain_events()
        await membership_repo.update(membership)

        found = await membership_repo.get_by_id(membership.id)
        assert found is not None
        assert len(found.members) == 2

    async def test_update_remove_member(self, membership_repo: SqlProjectMembershipRepository, make_project, make_user) -> None:
        proj = await make_project()
        owner_id = proj.owner_ids[0] if proj.owner_ids else Id.generate()
        membership = ProjectMembership.create(project_id=proj.id, owner_id=owner_id)
        membership.clear_domain_events()
        await membership_repo.add(membership)

        new_user = await make_user()
        membership.add_member(user_id=new_user.id, role_id=Id.generate())
        membership.clear_domain_events()
        await membership_repo.update(membership)

        membership.remove_member(new_user.id, is_owner=False)
        membership.clear_domain_events()
        await membership_repo.update(membership)

        found = await membership_repo.get_by_id(membership.id)
        assert found is not None
        assert len(found.members) == 1


@pytest.mark.integration
class TestSqlProjectMembershipRepositoryDelete:
    """Тесты удаления."""

    async def test_delete(self, membership_repo: SqlProjectMembershipRepository, make_project) -> None:
        proj = await make_project()
        owner_id = proj.owner_ids[0] if proj.owner_ids else Id.generate()
        membership = ProjectMembership.create(project_id=proj.id, owner_id=owner_id)
        membership.clear_domain_events()
        await membership_repo.add(membership)

        await membership_repo.delete(membership.id)
        found = await membership_repo.get_by_id(membership.id)
        assert found is None
