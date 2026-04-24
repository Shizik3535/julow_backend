"""Unit-тесты для WorkspaceLimits (Workspace BC)."""

import pytest

from app.shared.domain.exceptions import ValidationException
from app.context.workspace.domain.value_objects.workspace_limits import WorkspaceLimits


@pytest.mark.unit
class TestWorkspaceLimits:
    def test_defaults_all_none(self) -> None:
        limits = WorkspaceLimits()
        assert limits.max_projects is None
        assert limits.max_members is None
        assert limits.max_storage_bytes is None
        assert limits.max_file_size_bytes is None
        assert limits.max_teams is None

    def test_custom_values(self) -> None:
        limits = WorkspaceLimits(
            max_projects=10,
            max_members=50,
            max_storage_bytes=1_000_000,
            max_file_size_bytes=100_000,
            max_teams=5,
        )
        assert limits.max_projects == 10
        assert limits.max_members == 50

    def test_negative_max_projects_raises(self) -> None:
        with pytest.raises(ValidationException) as exc_info:
            WorkspaceLimits(max_projects=-1)
        assert exc_info.value.field == "max_projects"

    def test_negative_max_members_raises(self) -> None:
        with pytest.raises(ValidationException) as exc_info:
            WorkspaceLimits(max_members=-1)
        assert exc_info.value.field == "max_members"

    def test_negative_max_storage_raises(self) -> None:
        with pytest.raises(ValidationException) as exc_info:
            WorkspaceLimits(max_storage_bytes=-1)
        assert exc_info.value.field == "max_storage_bytes"

    def test_negative_max_file_size_raises(self) -> None:
        with pytest.raises(ValidationException) as exc_info:
            WorkspaceLimits(max_file_size_bytes=-1)
        assert exc_info.value.field == "max_file_size_bytes"

    def test_negative_max_teams_raises(self) -> None:
        with pytest.raises(ValidationException) as exc_info:
            WorkspaceLimits(max_teams=-1)
        assert exc_info.value.field == "max_teams"

    def test_zero_is_valid(self) -> None:
        limits = WorkspaceLimits(max_projects=0)
        assert limits.max_projects == 0

    def test_frozen(self) -> None:
        limits = WorkspaceLimits()
        with pytest.raises(AttributeError):
            limits.max_projects = 10  # type: ignore[misc]

    def test_equality_by_value(self) -> None:
        assert WorkspaceLimits() == WorkspaceLimits()
