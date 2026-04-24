from __future__ import annotations

from abc import ABC, abstractmethod

from app.shared.application.ports.file_storage.file_storage_dto import FileInfo


class FileStoragePort(ABC):
    """
    Порт (интерфейс) для файлового хранилища.

    Абстрагирует работу с S3-совместимыми хранилищами
    (AWS S3, MinIO, Yandex Object Storage и т.д.).
    Application-слой зависит от этого порта, infrastructure-слой реализует.

    Методы:
        upload: Загрузить файл.
        download: Скачать файл.
        delete: Удалить файл.
        get_info: Получить информацию о файле.
        get_url: Получить подписанный URL для доступа к файлу.

    Правила:
        - Файлы идентифицируются по ключу (key)
        - Хранилище не интерпретирует содержимое файлов
        - Подписанные URL генерируются с ограниченным временем жизни
    """

    @abstractmethod
    async def upload(self, key: str, data: bytes, content_type: str = "application/octet-stream") -> FileInfo:
        """
        Загрузить файл в хранилище.

        Аргументы:
            key: Ключ файла в хранилище.
            data: Содержимое файла.
            content_type: MIME-тип файла.

        Возвращает:
            Информация о загруженном файле.
        """

    @abstractmethod
    async def download(self, key: str) -> bytes:
        """
        Скачать файл из хранилища.

        Аргументы:
            key: Ключ файла в хранилище.

        Возвращает:
            Содержимое файла в виде байтов.
        """

    @abstractmethod
    async def delete(self, key: str) -> None:
        """
        Удалить файл из хранилища.

        Аргументы:
            key: Ключ файла в хранилище.
        """

    @abstractmethod
    async def get_info(self, key: str) -> FileInfo | None:
        """
        Получить информацию о файле.

        Аргументы:
            key: Ключ файла в хранилище.

        Возвращает:
            FileInfo или None, если файл не найден.
        """

    @abstractmethod
    async def get_url(self, key: str, expires_in: int | None = 3600) -> str:
        """
        Получить URL для доступа к файлу.

        Аргументы:
            key: Ключ файла в хранилище.
            expires_in: Время жизни URL в секундах.
                None — бессрочный URL (публичный доступ).

        Возвращает:
            URL для доступа к файлу (подписанный или публичный).
        """
