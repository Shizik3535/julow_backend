"""Unit-тесты для WorkspaceBranding (Workspace BC)."""

import pytest

from app.shared.domain.value_objects.url_vo import Url
from app.context.workspace.domain.value_objects.workspace_branding import WorkspaceBranding


@pytest.mark.unit
class TestWorkspaceBranding:
    def test_defaults(self) -> None:
        branding = WorkspaceBranding()
        assert branding.logo_url is None
        assert branding.cover_image_url is None
        assert branding.custom_css is None

    def test_custom_values(self) -> None:
        logo = Url("https://example.com/logo.png")
        cover = Url("https://example.com/cover.png")
        branding = WorkspaceBranding(
            logo_url=logo,
            cover_image_url=cover,
            custom_css="body { color: red; }",
        )
        assert branding.logo_url == logo
        assert branding.cover_image_url == cover
        assert branding.custom_css == "body { color: red; }"

    def test_frozen(self) -> None:
        branding = WorkspaceBranding()
        with pytest.raises(AttributeError):
            branding.custom_css = "new"  # type: ignore[misc]

    def test_equality_by_value(self) -> None:
        assert WorkspaceBranding() == WorkspaceBranding()
