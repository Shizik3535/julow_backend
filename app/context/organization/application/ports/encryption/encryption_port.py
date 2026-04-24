from __future__ import annotations

from abc import ABC, abstractmethod


class EncryptionPort(ABC):
    """
    Порт для шифрования и дешифрования данных.

    Используется Organization BC для шифрования SSO-сертификатов
    и ключей доступа к хранилищу (StorageConfig.access_key,
    SSOIntegration.certificate).

    Реализация размещается в infrastructure-слое Organization BC.
    """

    @abstractmethod
    async def encrypt(self, plaintext: str) -> str:
        """
        Зашифровать текст.

        Аргументы:
            plaintext: Открытый текст.

        Возвращает:
            Зашифрованная строка.
        """

    @abstractmethod
    async def decrypt(self, ciphertext: str) -> str:
        """
        Расшифровать текст.

        Аргументы:
            ciphertext: Зашифрованная строка.

        Возвращает:
            Расшифрованный открытый текст.
        """
