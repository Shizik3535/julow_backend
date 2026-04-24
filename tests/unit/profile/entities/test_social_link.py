"""Unit-тесты для SocialLink."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.shared.domain.value_objects.url_vo import Url
from app.shared.domain.exceptions import ValidationException
from app.context.profile.domain.entities.social_link import SocialLink


@pytest.mark.unit
class TestSocialLink:
    def test_create_social_link(self) -> None:
        link = SocialLink(platform="github", url=Url("https://github.com/user"))
        assert link.platform == "github"
        assert link.url == Url("https://github.com/user")
        assert link.display_name is None

    def test_create_with_display_name(self) -> None:
        link = SocialLink(platform="linkedin", url=Url("https://linkedin.com/in/user"), display_name="My LinkedIn")
        assert link.display_name == "My LinkedIn"

    def test_equality_by_id(self) -> None:
        shared_id = Id.generate()
        l1 = SocialLink(id=shared_id, platform="github", url=Url("https://github.com/user"))
        l2 = SocialLink(id=shared_id, platform="github", url=Url("https://github.com/user"))
        assert l1 == l2

    def test_inequality_different_id(self) -> None:
        l1 = SocialLink(platform="github", url=Url("https://github.com/user"))
        l2 = SocialLink(platform="github", url=Url("https://github.com/user"))
        assert l1 != l2

    def test_invalid_url_raises(self) -> None:
        with pytest.raises(Exception):
            SocialLink(platform="github", url=Url("not-a-url"))

    def test_empty_platform_raises(self) -> None:
        with pytest.raises(ValidationException):
            SocialLink(platform="", url=Url("https://github.com/user"))

    def test_blank_platform_raises(self) -> None:
        with pytest.raises(ValidationException):
            SocialLink(platform="   ", url=Url("https://github.com/user"))
