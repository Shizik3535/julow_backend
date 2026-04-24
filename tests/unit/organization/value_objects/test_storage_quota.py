"""Unit-тесты для StorageQuota (Organization BC)."""

import pytest

from app.shared.domain.exceptions import ValidationException
from app.context.organization.domain.value_objects.storage_quota import StorageQuota


@pytest.mark.unit
class TestStorageQuota:
    def test_defaults(self) -> None:
        quota = StorageQuota()
        assert quota.max_bytes == 0
        assert quota.used_bytes == 0
        assert quota.max_file_size_bytes is None
        assert quota.allowed_extensions is None

    def test_custom_values(self) -> None:
        quota = StorageQuota(
            max_bytes=1_000_000,
            used_bytes=500_000,
            max_file_size_bytes=10_000,
            allowed_extensions=[".pdf", ".docx"],
        )
        assert quota.max_bytes == 1_000_000
        assert quota.used_bytes == 500_000

    def test_negative_max_bytes_raises(self) -> None:
        with pytest.raises(ValidationException) as exc_info:
            StorageQuota(max_bytes=-1)
        assert exc_info.value.field == "max_bytes"

    def test_negative_used_bytes_raises(self) -> None:
        with pytest.raises(ValidationException) as exc_info:
            StorageQuota(used_bytes=-1)
        assert exc_info.value.field == "used_bytes"

    def test_used_exceeds_max_raises(self) -> None:
        with pytest.raises(ValidationException) as exc_info:
            StorageQuota(max_bytes=100, used_bytes=200)
        assert exc_info.value.field == "used_bytes"

    def test_negative_max_file_size_raises(self) -> None:
        with pytest.raises(ValidationException) as exc_info:
            StorageQuota(max_file_size_bytes=-1)
        assert exc_info.value.field == "max_file_size_bytes"

    def test_frozen(self) -> None:
        quota = StorageQuota()
        with pytest.raises(AttributeError):
            quota.max_bytes = 999  # type: ignore[misc]

    def test_equality_by_value(self) -> None:
        assert StorageQuota() == StorageQuota()
