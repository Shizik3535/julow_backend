"""Unit-тесты для ProfileVisibility."""

import pytest

from app.context.profile.domain.value_objects.profile_visibility import ProfileVisibility


@pytest.mark.unit
class TestProfileVisibility:
    def test_all_visibilities_exist(self) -> None:
        assert ProfileVisibility.PUBLIC.value == "public"
        assert ProfileVisibility.ORGANIZATION_ONLY.value == "organization_only"
        assert ProfileVisibility.PRIVATE.value == "private"

    def test_visibilities_are_distinct(self) -> None:
        values = [v.value for v in ProfileVisibility]
        assert len(values) == len(set(values))
