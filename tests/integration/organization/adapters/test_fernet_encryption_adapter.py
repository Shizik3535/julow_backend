"""Интеграционные тесты FernetEncryptionAdapter (реальная библиотека cryptography)."""

import pytest

from cryptography.fernet import Fernet, InvalidToken

from app.context.organization.infrastructure.encryption.fernet_encryption_adapter import (
    FernetEncryptionAdapter,
)


@pytest.mark.integration
class TestFernetEncryptionAdapter:
    """Тесты шифрования/дешифрования Fernet."""

    @pytest.fixture
    def adapter(self) -> FernetEncryptionAdapter:
        key = Fernet.generate_key().decode()
        return FernetEncryptionAdapter(encryption_key=key)

    async def test_encrypt_decrypt_roundtrip(self, adapter) -> None:
        plaintext = "my-secret-certificate"
        ciphertext = await adapter.encrypt(plaintext)
        decrypted = await adapter.decrypt(ciphertext)
        assert decrypted == plaintext

    async def test_encrypt_produces_different_ciphertext(self, adapter) -> None:
        plaintext = "same-input"
        ct1 = await adapter.encrypt(plaintext)
        ct2 = await adapter.encrypt(plaintext)
        assert ct1 != ct2  # Fernet uses random IV

    async def test_decrypt_invalid_token_raises(self, adapter) -> None:
        with pytest.raises(InvalidToken):
            await adapter.decrypt("invalid-ciphertext==")

    async def test_encrypt_decrypt_empty_string(self, adapter) -> None:
        ciphertext = await adapter.encrypt("")
        decrypted = await adapter.decrypt(ciphertext)
        assert decrypted == ""
