"""Unit-тесты для WorkspacePersonalization (Workspace BC)."""

import pytest

from app.shared.domain.value_objects.color_vo import Color
from app.context.workspace.domain.value_objects.workspace_branding import WorkspaceBranding
from app.context.workspace.domain.value_objects.workspace_personalization import WorkspacePersonalization


@pytest.mark.unit
class TestWorkspacePersonalization:
    def test_defaults(self) -> None:
        pers = WorkspacePersonalization()
        assert pers.color is None
        assert pers.icon is None
        assert pers.display_name is None
        assert pers.description is None
        assert pers.branding is None

    def test_custom_values(self) -> None:
        color = Color("#FF5500")
        icon = "Code"
        branding = WorkspaceBranding(custom_css="body {}")
        pers = WorkspacePersonalization(
            color=color,
            icon=icon,
            display_name="My WS",
            description="Desc",
            branding=branding,
        )
        assert pers.color == color
        assert pers.icon == icon
        assert pers.display_name == "My WS"
        assert pers.description == "Desc"
        assert pers.branding == branding

    def test_frozen(self) -> None:
        pers = WorkspacePersonalization()
        with pytest.raises(AttributeError):
            pers.display_name = "new"  # type: ignore[misc]

    def test_equality_by_value(self) -> None:
        assert WorkspacePersonalization() == WorkspacePersonalization()
