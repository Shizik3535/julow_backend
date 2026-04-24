"""Unit-тесты для OrgPersonalization (Organization BC)."""

import pytest

from app.shared.domain.value_objects.url_vo import Url
from app.context.organization.domain.value_objects.accent_color import AccentColor
from app.context.organization.domain.value_objects.org_branding import OrgBranding
from app.context.organization.domain.value_objects.org_personalization import OrgPersonalization


@pytest.mark.unit
class TestOrgPersonalization:
    def test_defaults(self) -> None:
        pers = OrgPersonalization()
        assert pers.color is None
        assert pers.icon_url is None
        assert pers.display_name is None
        assert pers.custom_domain is None
        assert pers.branding is None

    def test_custom_values(self) -> None:
        branding = OrgBranding(login_message="Hello")
        pers = OrgPersonalization(
            color=AccentColor("#6366F1"),
            icon_url=Url("https://example.com/icon.png"),
            display_name="My Org",
            custom_domain="org.example.com",
            branding=branding,
        )
        assert pers.color is not None
        assert pers.display_name == "My Org"
        assert pers.branding is not None
        assert pers.branding.login_message == "Hello"

    def test_frozen(self) -> None:
        pers = OrgPersonalization()
        with pytest.raises(AttributeError):
            pers.display_name = "changed"  # type: ignore[misc]

    def test_equality_by_value(self) -> None:
        assert OrgPersonalization() == OrgPersonalization()
