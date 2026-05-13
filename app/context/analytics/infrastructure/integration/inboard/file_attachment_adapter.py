from __future__ import annotations

from app.context.analytics.application.ports.integration.inboard.file_attachment_port import (
    FileAttachmentPort,
    ReportAttachmentUploadResult,
)
from app.context.filestorage.application.ports.integration.outboard.file_attachment_provider import (
    FileAttachmentProvider,
)


class FileAttachmentAdapter(FileAttachmentPort):
    """
    Реализация ``FileAttachmentPort`` для Analytics BC.

    Делегирует в outboard ``FileAttachmentProvider`` (FileStorage BC),
    благодаря чему готовый файл отчёта попадает в FileStorage как
    обычный агрегат ``File`` (с учётом квоты, событий, антивируса и т. д.).
    """

    def __init__(self, provider: FileAttachmentProvider) -> None:
        self._provider = provider

    async def upload_report(
        self,
        *,
        workspace_id: str,
        uploader_id: str,
        filename: str,
        file_data: bytes,
        content_type: str,
    ) -> ReportAttachmentUploadResult:
        result = await self._provider.upload_attachment(
            workspace_id=workspace_id,
            uploader_id=uploader_id,
            filename=filename,
            file_data=file_data,
            content_type=content_type,
        )
        return ReportAttachmentUploadResult(
            file_id=result.file_id,
            url=result.url,
            storage_path=result.storage_path,
            size_bytes=result.size_bytes,
        )

    async def get_report_url(
        self, file_id: str, expires_in: int | None = 3600
    ) -> str | None:
        return await self._provider.get_attachment_url(
            file_id=file_id, expires_in=expires_in
        )

    async def delete_report(self, file_id: str) -> None:
        await self._provider.delete_attachment(file_id=file_id)
