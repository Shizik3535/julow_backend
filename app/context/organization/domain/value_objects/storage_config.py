from __future__ import annotations

from dataclasses import dataclass

from app.shared.domain.base_value_object import ValueObject
from app.shared.domain.exceptions import ValidationException
from app.shared.domain.value_objects.url_vo import Url
from app.context.organization.domain.value_objects.storage_provider import StorageProvider


@dataclass(frozen=True)
class StorageConfig(ValueObject):
    """
    Конфигурация хранилища организации.

    Атрибуты:
        provider: Провайдер хранилища.
        endpoint: URL эндпоинта.
        bucket: Имя бакета.
        region: Регион.
        access_key: Ключ доступа (зашифрованный).
    """

    provider: StorageProvider = StorageProvider.LOCAL
    endpoint: Url | None = None
    bucket: str = ""
    region: str = ""
    access_key: str = ""

    def __post_init__(self) -> None:
        if self.provider != StorageProvider.LOCAL:
            if not self.bucket:
                raise ValidationException(
                    field="bucket",
                    message="Имя бакета не может быть пустым",
                )
            if not self.region:
                raise ValidationException(
                    field="region",
                    message="Регион не может быть пустым",
                )
            if not self.access_key:
                raise ValidationException(
                    field="access_key",
                    message="Ключ доступа не может быть пустым",
                )
