"""Unit-тесты для StorageConfig (Organization BC)."""

import pytest

from app.shared.domain.exceptions import ValidationException
from app.shared.domain.value_objects.url_vo import Url
from app.context.organization.domain.value_objects.storage_config import StorageConfig
from app.context.organization.domain.value_objects.storage_provider import StorageProvider


@pytest.mark.unit
class TestStorageConfig:
    def test_defaults_local_provider(self) -> None:
        config = StorageConfig()
        assert config.provider == StorageProvider.LOCAL
        assert config.bucket == ""
        assert config.region == ""
        assert config.access_key == ""

    def test_custom_values(self) -> None:
        config = StorageConfig(
            provider=StorageProvider.AWS_S3,
            endpoint=Url("https://s3.amazonaws.com"),
            bucket="my-bucket",
            region="us-east-1",
            access_key="AKIAIOSFODNN7EXAMPLE",
        )
        assert config.provider == StorageProvider.AWS_S3
        assert config.bucket == "my-bucket"

    def test_non_local_provider_without_bucket_raises(self) -> None:
        with pytest.raises(ValidationException) as exc_info:
            StorageConfig(provider=StorageProvider.AWS_S3, bucket="", region="us-east-1", access_key="key")
        assert exc_info.value.field == "bucket"

    def test_non_local_provider_without_region_raises(self) -> None:
        with pytest.raises(ValidationException) as exc_info:
            StorageConfig(provider=StorageProvider.AWS_S3, bucket="bucket", region="", access_key="key")
        assert exc_info.value.field == "region"

    def test_non_local_provider_without_access_key_raises(self) -> None:
        with pytest.raises(ValidationException) as exc_info:
            StorageConfig(provider=StorageProvider.AWS_S3, bucket="bucket", region="us-east-1", access_key="")
        assert exc_info.value.field == "access_key"

    def test_local_provider_allows_empty_fields(self) -> None:
        config = StorageConfig(provider=StorageProvider.LOCAL)
        assert config.bucket == ""

    def test_frozen(self) -> None:
        config = StorageConfig()
        with pytest.raises(AttributeError):
            config.bucket = "changed"  # type: ignore[misc]

    def test_equality_by_value(self) -> None:
        assert StorageConfig() == StorageConfig()
