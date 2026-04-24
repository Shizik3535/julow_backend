"""Unit-тесты для OnlineStatusVisibility."""

import pytest

from app.context.profile.domain.value_objects.online_status_visibility import OnlineStatusVisibility


@pytest.mark.unit
class TestOnlineStatusVisibility:
    def test_all_visibilities_exist(self) -> None:
        assert OnlineStatusVisibility.EVERYONE.value == "everyone"
        assert OnlineStatusVisibility.CONTACTS_ONLY.value == "contacts_only"
        assert OnlineStatusVisibility.NOBODY.value == "nobody"

    def test_visibilities_are_distinct(self) -> None:
        values = [v.value for v in OnlineStatusVisibility]
        assert len(values) == len(set(values))
