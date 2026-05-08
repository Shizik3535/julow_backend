from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.shared.domain.base_aggregate import AggregateRoot
from app.shared.domain.value_objects.id_vo import Id
from app.context.filestorage.domain.value_objects.storage_owner_type import StorageOwnerType
from app.context.filestorage.domain.value_objects.storage_provider import StorageProvider
from app.context.filestorage.domain.value_objects.storage_config import StorageConfig
from app.context.filestorage.domain.value_objects.file_type import FileType
from app.context.filestorage.domain.events.storage_events import (
    StorageQuotaApproaching,
)
from app.context.filestorage.domain.exceptions.storage_exceptions import (
    StorageQuotaExceededException,
)


@dataclass
class Storage(AggregateRoot):
    """
    Корень агрегата хранилища (FileStorage BC).

    Атрибуты:
        owner_type: Тип владельца.
        owner_id: Opaque ID владельца.
        provider: Провайдер хранилища.
        config: Конфигурация провайдера.
        max_bytes: Максимальный объём в байтах.
        used_bytes: Использованный объём в байтах.
        allowed_file_types: Разрешённые типы файлов (None = все).
        max_file_size_bytes: Макс. размер одного файла (None = без лимита).
        is_encrypted: Шифрование включено.
        created_at: Время создания.
        updated_at: Время последнего обновления.
    """

    owner_type: StorageOwnerType = StorageOwnerType.WORKSPACE
    owner_id: Id = field(default_factory=Id.generate)
    provider: StorageProvider = StorageProvider.LOCAL
    config: StorageConfig = field(default_factory=StorageConfig)
    max_bytes: int = 0
    used_bytes: int = 0
    allowed_file_types: list[FileType] | None = None
    max_file_size_bytes: int | None = None
    is_encrypted: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))

    @classmethod
    def create(
        cls,
        owner_type: StorageOwnerType,
        owner_id: Id,
        provider: StorageProvider,
        config: StorageConfig,
        max_bytes: int,
    ) -> Storage:
        """Создаёт хранилище."""
        return cls(
            owner_type=owner_type,
            owner_id=owner_id,
            provider=provider,
            config=config,
            max_bytes=max_bytes,
        )

    # --- Квоты ---

    def add_usage(self, bytes_count: int) -> None:
        """Добавляет использование, проверяет квоту."""
        new_used = self.used_bytes + bytes_count
        if new_used > self.max_bytes:
            raise StorageQuotaExceededException(
                max_bytes=self.max_bytes,
                used_bytes=new_used,
            )
        self.used_bytes = new_used
        self.updated_at = datetime.now(tz=timezone.utc)
        # Проверка порога 90%
        if self.max_bytes > 0 and self.used_bytes / self.max_bytes >= 0.9:
            used_percent = int(self.used_bytes / self.max_bytes * 100)
            self._register_event(
                StorageQuotaApproaching(
                    storage_id=str(self.id),
                    used_percent=used_percent,
                )
            )

    def remove_usage(self, bytes_count: int) -> None:
        """Уменьшает использование."""
        self.used_bytes = max(0, self.used_bytes - bytes_count)
        self.updated_at = datetime.now(tz=timezone.utc)

    # --- Настройки ---

    def update_config(self, config: StorageConfig) -> None:
        self.config = config
        self.updated_at = datetime.now(tz=timezone.utc)

    def update_quota(self, max_bytes: int) -> None:
        self.max_bytes = max_bytes
        self.updated_at = datetime.now(tz=timezone.utc)

    def set_allowed_file_types(self, file_types: list[FileType] | None) -> None:
        self.allowed_file_types = file_types
        self.updated_at = datetime.now(tz=timezone.utc)

    def set_max_file_size(self, max_size_bytes: int | None) -> None:
        self.max_file_size_bytes = max_size_bytes
        self.updated_at = datetime.now(tz=timezone.utc)

    def enable_encryption(self) -> None:
        self.is_encrypted = True
        self.updated_at = datetime.now(tz=timezone.utc)

    def disable_encryption(self) -> None:
        self.is_encrypted = False
        self.updated_at = datetime.now(tz=timezone.utc)
