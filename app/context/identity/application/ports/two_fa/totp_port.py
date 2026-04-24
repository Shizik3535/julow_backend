from __future__ import annotations

from abc import ABC, abstractmethod


class TOTPPort(ABC):
    """
    BC-специфичный порт для работы с TOTP (Time-based One-Time Password).

    Абстрагирует генерацию секретов, создание provisioning URI
    для QR-кодов и верификацию одноразовых кодов.

    Реализация (адаптер) находится в infrastructure-слое Identity BC.
    """

    @abstractmethod
    def generate_secret(self) -> str:
        """
        Сгенерировать новый TOTP-секрет.

        Возвращает:
            Base32-encoded секрет.
        """

    @abstractmethod
    def get_provisioning_uri(self, secret: str, email: str, issuer: str) -> str:
        """
        Создать provisioning URI для TOTP (для генерации QR-кода).

        Аргументы:
            secret: TOTP-секрет (base32).
            email: Email пользователя (используется как account name).
            issuer: Имя приложения/сервиса.

        Возвращает:
            otpauth:// URI.
        """

    @abstractmethod
    def verify_code(self, secret: str, code: str) -> bool:
        """
        Проверить TOTP-код.

        Аргументы:
            secret: TOTP-секрет (base32).
            code: Одноразовый код от пользователя.

        Возвращает:
            True, если код валиден.
        """
