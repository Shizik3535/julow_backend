"""Unit-тесты для ProjectView (Project BC)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.project.domain.entities.project_view import ProjectView
from app.context.project.domain.value_objects.project_view_config import ProjectViewConfig
from app.context.project.domain.value_objects.view_type import ViewType


@pytest.mark.unit
class TestProjectView:
    def test_create(self) -> None:
        view = ProjectView(name="My Board")
        assert view.name == "My Board"
        assert view.id is not None
        assert view.is_default is False
        assert view.is_shared is True
        assert view.owner_id is None

    def test_create_with_config(self) -> None:
        config = ProjectViewConfig(view_type=ViewType.LIST)
        view = ProjectView(name="List View", config=config, is_shared=False, owner_id=Id.generate())
        assert view.config.view_type == ViewType.LIST
        assert not view.is_shared
        assert view.owner_id is not None

    def test_equality_by_id(self) -> None:
        shared_id = Id.generate()
        v1 = ProjectView(id=shared_id, name="View")
        v2 = ProjectView(id=shared_id, name="View")
        assert v1 == v2

    def test_inequality_different_id(self) -> None:
        v1 = ProjectView(name="View")
        v2 = ProjectView(name="View")
        assert v1 != v2
