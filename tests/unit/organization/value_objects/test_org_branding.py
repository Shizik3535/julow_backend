"""Unit-тесты для OrgBranding (Organization BC)."""

import pytest

from app.shared.domain.value_objects.url_vo import Url
from app.context.organization.domain.value_objects.org_branding import OrgBranding


@pytest.mark.unit
class TestOrgBranding:
    def test_defaults(self) -> None:
        branding = OrgBranding()
        assert branding.logo_url is None
        assert branding.favicon_url is None
        assert branding.custom_css is None
        assert branding.login_message is None

    def test_custom_values(self) -> None:
        branding = OrgBranding(
            logo_url=Url("https://example.com/logo.png"),
            favicon_url=Url("https://example.com/favicon.ico"),
            custom_css="body { color: red; }",
            login_message="Welcome!",
        )
        assert branding.logo_url is not None
        assert branding.custom_css == "body { color: red; }"
        assert branding.login_message == "Welcome!"

    def test_frozen(self) -> None:
        branding = OrgBranding()
        with pytest.raises(AttributeError):
            branding.custom_css = "changed"  # type: ignore[misc]

    def test_equality_by_value(self) -> None:
        assert OrgBranding() == OrgBranding()
