from __future__ import annotations

from dataclasses import dataclass, field

from app.shared.domain.base_value_object import ValueObject


@dataclass(frozen=True)
class StorageConfig(ValueObject):
    """
    Конфигурация провайдера хранилища.

    Credentials хранятся по ссылкам (ref), не в открытом виде.

    Атрибуты:
        endpoint: URL endpoint (для S3-совместимых).
        bucket: Имя бакета.
        region: Регион.
        access_key_ref: Ссылка на секрет (vault).
        secret_key_ref: Ссылка на секрет (vault).
        custom_params: Провайдер-специфичные настройки.
    """

    endpoint: str | None = None
    bucket: str | None = None
    region: str | None = None
    access_key_ref: str | None = None
    secret_key_ref: str | None = None
    custom_params: dict[str, str] | None = None
