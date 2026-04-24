from __future__ import annotations

from enum import Enum


class EncryptionAlgorithm(Enum):
    AES_256_GCM = "aes_256_gcm"
    AES_256_CBC = "aes_256_cbc"
    CHACHA20_POLY1305 = "chacha20_poly1305"
