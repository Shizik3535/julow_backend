from __future__ import annotations

from cryptography.fernet import Fernet

from app.context.organization.application.ports.encryption.encryption_port import EncryptionPort


class FernetEncryptionAdapter(EncryptionPort):
    """
    Реализация EncryptionPort на основе Fernet (symmetric encryption).

    Используется для шифрования SSO-сертификатов и ключей доступа
    к хранилищу (StorageConfig.access_key, SSOIntegration.certificate).
    """

    def __init__(self, encryption_key: str) -> None:
        self._fernet = Fernet(encryption_key.encode() if isinstance(encryption_key, str) else encryption_key)

    async def encrypt(self, plaintext: str) -> str:
        return self._fernet.encrypt(plaintext.encode()).decode()

    async def decrypt(self, ciphertext: str) -> str:
        return self._fernet.decrypt(ciphertext.encode()).decode()
