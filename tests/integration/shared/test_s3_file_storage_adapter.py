"""Интеграционные тесты S3FileStorageAdapter (реальный MinIO)."""

import pytest

from aiobotocore.session import AioSession

from app.shared.infrastructure.file_storage.s3_file_storage_adapter import S3FileStorageAdapter


@pytest.mark.integration
class TestS3FileStorageAdapter:
    """Тесты файлового хранилища через MinIO (S3-совместимый)."""

    @pytest.fixture
    def adapter(self, s3_session: AioSession, s3_client_kwargs: dict, s3_test_bucket: str) -> S3FileStorageAdapter:
        return S3FileStorageAdapter(
            session=s3_session,
            client_kwargs=s3_client_kwargs,
            bucket_name=s3_test_bucket,
            public_url_base="http://localhost:9000",
        )

    async def test_upload_and_download(self, adapter: S3FileStorageAdapter) -> None:
        content = b"Hello, MinIO!"
        info = await adapter.upload("test/hello.txt", content, content_type="text/plain")
        assert info.key == "test/hello.txt"
        assert info.size == len(content)

        downloaded = await adapter.download("test/hello.txt")
        assert downloaded == content

    async def test_get_info(self, adapter: S3FileStorageAdapter) -> None:
        await adapter.upload("info-test.bin", b"\x00\x01\x02", content_type="application/octet-stream")
        info = await adapter.get_info("info-test.bin")
        assert info is not None
        assert info.key == "info-test.bin"
        assert info.size == 3

    async def test_get_info_missing_returns_none(self, adapter: S3FileStorageAdapter) -> None:
        info = await adapter.get_info("does-not-exist.txt")
        assert info is None

    async def test_delete(self, adapter: S3FileStorageAdapter) -> None:
        await adapter.upload("to-delete.txt", b"data")
        await adapter.delete("to-delete.txt")
        info = await adapter.get_info("to-delete.txt")
        assert info is None

    async def test_get_presigned_url(self, adapter: S3FileStorageAdapter) -> None:
        await adapter.upload("url-test.txt", b"url content")
        url = await adapter.get_url("url-test.txt", expires_in=300)
        assert "url-test.txt" in url
        assert url.startswith("http")

    async def test_get_public_url(self, adapter: S3FileStorageAdapter) -> None:
        url = await adapter.get_url("public-file.txt", expires_in=None)
        assert "public-file.txt" in url

    async def test_upload_large_file(self, adapter: S3FileStorageAdapter) -> None:
        content = b"x" * 1024 * 100  # 100 KB
        info = await adapter.upload("large.bin", content)
        assert info.size == 1024 * 100
        downloaded = await adapter.download("large.bin")
        assert len(downloaded) == 1024 * 100
