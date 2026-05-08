from __future__ import annotations

from app.context.communication.application.ports.integration.inboard.file_attachment_port import (
    CommunicationAttachmentUploadResult,
    FileAttachmentPort,
)
from app.context.filestorage.application.ports.integration.outboard.file_attachment_provider import (
    FileAttachmentProvider,
)


class FileAttachmentAdapter(FileAttachmentPort):
    """
    Реализация FileAttachmentPort для Communication BC.

    Делегирует в FileAttachmentProvider (outboard FileStorage BC).
    """

    def __init__(self, provider: FileAttachmentProvider) -> None:
        self._provider = provider

    async def upload_attachment(
        self,
        *,
        workspace_id: str,
        uploader_id: str,
        filename: str,
        file_data: bytes,
        content_type: str,
    ) -> CommunicationAttachmentUploadResult:
        result = await self._provider.upload_attachment(
            workspace_id=workspace_id,
            uploader_id=uploader_id,
            filename=filename,
            file_data=file_data,
            content_type=content_type,
        )
        return CommunicationAttachmentUploadResult(
            file_id=result.file_id,
            url=result.url,
            storage_path=result.storage_path,
            size_bytes=result.size_bytes,
        )

    async def delete_attachment(self, file_id: str) -> None:
        await self._provider.delete_attachment(file_id)
