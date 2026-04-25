"""Интеграционные тесты SqlTaskTemplateRepository (реальная PostgreSQL)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.task.domain.value_objects.task_type import TaskType
from app.context.task.domain.value_objects.label import Label
from app.context.task.infrastructure.persistence.repositories.sql_task_template_repository import (
    SqlTaskTemplateRepository,
)


@pytest.mark.integration
class TestSqlTaskTemplateRepositoryAdd:
    """Тесты добавления."""

    async def test_add_and_get_by_id(
        self, task_template_repo: SqlTaskTemplateRepository, make_task_template
    ) -> None:
        template = await make_task_template()
        found = await task_template_repo.get_by_id(template.id)
        assert found is not None
        assert found.id == template.id

    async def test_add_persists_attributes(
        self, task_template_repo: SqlTaskTemplateRepository, make_task_template
    ) -> None:
        template = await make_task_template(name="Bug Report", task_type=TaskType.BUG)
        found = await task_template_repo.get_by_id(template.id)
        assert found is not None
        assert found.name == "Bug Report"
        assert found.task_type == TaskType.BUG
        assert found.is_system is False

    async def test_add_system_template(
        self, task_template_repo: SqlTaskTemplateRepository, make_task_template
    ) -> None:
        template = await make_task_template(name="System Template", is_system=True)
        found = await task_template_repo.get_by_id(template.id)
        assert found is not None
        assert found.is_system is True

    async def test_add_with_labels(
        self, task_template_repo: SqlTaskTemplateRepository, make_task_template
    ) -> None:
        labels = [Label(name="bug", color=None), Label(name="urgent", color=None)]
        template = await make_task_template(default_labels=labels)
        found = await task_template_repo.get_by_id(template.id)
        assert found is not None
        assert len(found.default_labels) == 2
        label_names = {l.name for l in found.default_labels}
        assert label_names == {"bug", "urgent"}

    async def test_add_with_checklists(
        self, task_template_repo: SqlTaskTemplateRepository, make_task_template
    ) -> None:
        from app.context.task.domain.entities.checklist import Checklist

        cl = Checklist(title="Steps")
        template = await make_task_template()
        template.default_checklists.append(cl)
        template.clear_domain_events()
        await task_template_repo.update(template)

        found = await task_template_repo.get_by_id(template.id)
        assert found is not None
        assert len(found.default_checklists) == 1
        assert found.default_checklists[0].title == "Steps"

    async def test_get_by_id_not_found(
        self, task_template_repo: SqlTaskTemplateRepository
    ) -> None:
        found = await task_template_repo.get_by_id(Id.generate())
        assert found is None


@pytest.mark.integration
class TestSqlTaskTemplateRepositorySearch:
    """Тесты поиска."""

    async def test_get_by_name_found(
        self, task_template_repo: SqlTaskTemplateRepository, make_task_template
    ) -> None:
        template = await make_task_template(name="FindMe")
        found = await task_template_repo.get_by_name("FindMe")
        assert found is not None
        assert found.id == template.id

    async def test_get_by_name_not_found(
        self, task_template_repo: SqlTaskTemplateRepository
    ) -> None:
        found = await task_template_repo.get_by_name("NonexistentTemplate")
        assert found is None

    async def test_get_system_templates(
        self, task_template_repo: SqlTaskTemplateRepository, make_task_template
    ) -> None:
        await make_task_template(name="SysTmpl1", is_system=True)
        await make_task_template(name="SysTmpl2", is_system=True)
        await make_task_template(name="CustomTmpl", is_system=False)

        system = await task_template_repo.get_system_templates()
        assert len(system) >= 2
        assert all(t.is_system for t in system)

    async def test_get_by_project(
        self, task_template_repo: SqlTaskTemplateRepository, make_task_template
    ) -> None:
        await make_task_template(name="ProjTmpl")
        results = await task_template_repo.get_by_project(Id.generate())
        assert len(results) >= 1


@pytest.mark.integration
class TestSqlTaskTemplateRepositoryUpdate:
    """Тесты обновления."""

    async def test_update_labels(
        self, task_template_repo: SqlTaskTemplateRepository, make_task_template
    ) -> None:
        template = await make_task_template()
        new_labels = [Label(name="updated", color=None)]
        template.update(default_labels=new_labels)
        template.clear_domain_events()
        await task_template_repo.update(template)

        found = await task_template_repo.get_by_id(template.id)
        assert found is not None
        assert len(found.default_labels) == 1
        assert found.default_labels[0].name == "updated"

    async def test_update_checklists(
        self, task_template_repo: SqlTaskTemplateRepository, make_task_template
    ) -> None:
        from app.context.task.domain.entities.checklist import Checklist

        template = await make_task_template()
        new_checklists = [Checklist(title="New Steps")]
        template.update(default_checklists=new_checklists)
        template.clear_domain_events()
        await task_template_repo.update(template)

        found = await task_template_repo.get_by_id(template.id)
        assert found is not None
        assert len(found.default_checklists) == 1
        assert found.default_checklists[0].title == "New Steps"

    async def test_update_custom_fields(
        self, task_template_repo: SqlTaskTemplateRepository, make_task_template
    ) -> None:
        template = await make_task_template()
        new_fields = {"priority": "high", "team": "backend"}
        template.update(default_custom_fields=new_fields)
        template.clear_domain_events()
        await task_template_repo.update(template)

        found = await task_template_repo.get_by_id(template.id)
        assert found is not None
        assert found.default_custom_fields == {"priority": "high", "team": "backend"}


@pytest.mark.integration
class TestSqlTaskTemplateRepositoryDelete:
    """Тесты удаления."""

    async def test_delete(
        self, task_template_repo: SqlTaskTemplateRepository, make_task_template
    ) -> None:
        template = await make_task_template()
        await task_template_repo.delete(template.id)
        found = await task_template_repo.get_by_id(template.id)
        assert found is None
