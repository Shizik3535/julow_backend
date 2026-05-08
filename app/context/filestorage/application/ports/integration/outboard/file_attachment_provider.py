from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class AttachmentUploadResult:
    """
    Результат загрузки файла-вложения через FileStorage BC.

    Атрибуты:
        file_id: UUID агрегата File в FileStorage BC.
        url: Публичная или подписанная ссылка для немедленного доступа.
        storage_path: Путь в blob-хранилище (для отладки/аудита).
        size_bytes: Размер файла.
    """

    file_id: str
    url: str
    storage_path: str
    size_bytes: int


class FileAttachmentProvider(ABC):
    """
    Outboard-порт: загрузка файлов-вложений через FileStorage BC.

    Реализуется в infrastructure-слое FileStorage BC. Используется
    Task BC, Communication BC (комментарии, сообщения) и другими BC
    для прикрепления файлов к своим сущностям.

    В отличие от прямого вызова ``FileStoragePort.upload`` (S3),
    этот порт **создаёт агрегат ``File``** в FileStorage BC:

    - Регистрирует файл в таблице ``fs_files`` (с владельцем, типом,
      статусом, scan_status и т.д.).
    - Учитывает квоту хранилища workspace
      (``StorageQuotaExceededException`` при превышении).
    - Эмитит доменное событие ``FileUploaded`` (для аналитики, антивируса,
      аудита).
    - Возвращает реальный ``file_id``, по которому файл доступен через
      FileStorage API (``GET /files/{id}``, скачивание, шаринг и т.д.).

    Авторизация на уровне consuming BC (Task/Communication) — этот port
    **не проверяет** ``files.write`` в workspace, поскольку доступ к
    задаче/комментарию уже подразумевает право прикрепить вложение.
    """

    @abstractmethod
    async def upload_attachment(
        self,
        *,
        workspace_id: str,
        uploader_id: str,
        filename: str,
        file_data: bytes,
        content_type: str,
        folder_id: str | None = None,
    ) -> AttachmentUploadResult:
        """
        Загрузить файл, создать агрегат ``File``, вернуть метаданные.

        Аргументы:
            workspace_id: ID workspace-владельца (для квоты и привязки).
            uploader_id: ID пользователя, загружающего файл.
            filename: Оригинальное имя файла.
            file_data: Содержимое.
            content_type: MIME-тип.
            folder_id: Опционально — папка назначения.

        Возвращает:
            ``AttachmentUploadResult`` с реальным ``file_id``.

        Выбрасывает:
            ``StorageQuotaExceededException``, ``FileTooLargeException``,
            ``FileTypeNotAllowedException``, ``StorageNotFoundException``.
        """

    @abstractmethod
    async def delete_attachment(self, file_id: str) -> None:
        """
        Окончательно удалить файл-вложение из FileStorage BC.

        Освобождает квоту, удаляет blob, эмитит ``FileDeleted``.
        Идемпотентно: если файл уже удалён или не найден — без ошибки.
        """

    @abstractmethod
    async def get_attachment_url(
        self, file_id: str, expires_in: int | None = 3600
    ) -> str | None:
        """
        Получить URL для скачивания вложения.

        Возвращает ``None``, если файл не найден.
        ``expires_in=None`` — публичный URL.
        """
