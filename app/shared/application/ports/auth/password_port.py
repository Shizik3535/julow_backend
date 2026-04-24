from __future__ import annotations

from abc import ABC, abstractmethod


class PasswordPort(ABC):
    """
    Порт (интерфейс) для работы с паролями.

    Абстрагирует хеширование и проверку паролей.
    Application-слой зависит от этого порта, infrastructure-слой реализует.

    Методы:
        hash_password: Захешировать пароль.
        verify_password: Проверить пароль против хеша.

    Правила:
        - Хеширование должно быть односторонним (необратимым)
        - Используется соль (salt) при хешировании
        - Верификация выполняется по постоянному времени (constant-time)
        - Методы синхронные (CPU-bound, нет I/O)
    """

    @abstractmethod
    def hash_password(self, password: str) -> str:
        """
        Захешировать пароль.

        Аргументы:
            password: Пароль в открытом виде.

        Возвращает:
            Хеш пароля.
        """

    @abstractmethod
    def verify_password(self, password: str, password_hash: str) -> bool:
        """
        Проверить пароль против хеша.

        Аргументы:
            password: Пароль в открытом виде.
            password_hash: Хеш для сравнения.

        Возвращает:
            True, если пароль совпадает с хешем.
        """
