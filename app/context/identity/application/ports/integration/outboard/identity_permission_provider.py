from __future__ import annotations

from abc import ABC, abstractmethod


class IdentityPermissionProvider(ABC):
    """
    Outboard-порт: предоставляет проверку разрешений другим BC.

    Другие BC инжектируют этот порт через DI для проверки,
    обладает ли пользователь указанным разрешением.
    Логика wildcard-матчинга («*», «users.*») инкапсулирована
    внутри Identity BC — потребителям не нужно её дублировать.

    Реализация находится в infrastructure-слое Identity BC.
    """

    @abstractmethod
    async def has_permission(self, user_id: str, permission: str) -> bool:
        """
        Проверяет, есть ли у пользователя указанное разрешение.

        Аргументы:
            user_id: Идентификатор пользователя.
            permission: Требуемое разрешение (например «users.write»).

        Возвращает:
            True, если разрешение есть, иначе False.
        """

    @abstractmethod
    async def require_permission(self, user_id: str, permission: str) -> None:
        """
        Проверяет разрешение и выбрасывает исключение при отсутствии.

        Аргументы:
            user_id: Идентификатор пользователя.
            permission: Требуемое разрешение.

        Raises:
            InsufficientPermissionsException: Если разрешение отсутствует.
        """
