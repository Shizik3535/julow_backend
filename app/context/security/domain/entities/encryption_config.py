from __future__ import annotations

from dataclasses import dataclass

from app.shared.domain.base_entity import BaseEntity
from app.context.security.domain.value_objects.encryption_algorithm import EncryptionAlgorithm


@dataclass
class EncryptionConfig(BaseEntity):
    algorithm: EncryptionAlgorithm = EncryptionAlgorithm.AES_256_GCM
    key_rotation_days: int | None = None
    is_at_rest: bool = True
    is_in_transit: bool = True
