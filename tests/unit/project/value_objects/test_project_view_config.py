"""Unit-тесты для ProjectViewConfig (Project BC)."""

import pytest

from app.context.project.domain.value_objects.project_view_config import ProjectViewConfig
from app.context.project.domain.value_objects.view_type import ViewType


@pytest.mark.unit
class TestProjectViewConfig:
    def test_defaults(self) -> None:
        config = ProjectViewConfig()
        assert config.view_type == ViewType.BOARD
        assert config.filters == []
        assert config.sorting == []
        assert config.grouping is None
        assert config.card_appearance is None
        assert config.column_settings is None

    def test_custom_values(self) -> None:
        config = ProjectViewConfig(
            view_type=ViewType.LIST,
            grouping="assignee",
            column_settings={"col1": "visible"},
        )
        assert config.view_type == ViewType.LIST
        assert config.grouping == "assignee"
        assert config.column_settings == {"col1": "visible"}

    def test_frozen(self) -> None:
        config = ProjectViewConfig()
        with pytest.raises(AttributeError):
            config.view_type = ViewType.TABLE  # type: ignore[misc]

    def test_equality_by_value(self) -> None:
        assert ProjectViewConfig() == ProjectViewConfig()

    def test_inequality_different_type(self) -> None:
        assert ProjectViewConfig() != ProjectViewConfig(view_type=ViewType.TABLE)
