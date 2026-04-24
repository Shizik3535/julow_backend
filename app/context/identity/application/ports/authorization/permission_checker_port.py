from __future__ import annotations

from abc import ABC, abstractmethod

from app.shared.domain.value_objects.id_vo import Id


class PermissionCheckerPort(ABC):
    """
    Порт проверки разрешений пользователя (Identity BC).

    Проверяет, обладает ли пользователь указанным разрешением
    на основе его ролей. Поддерживает wildcard-разрешения:
        - «*» — полный доступ
        - «users.*» — все разрешения в группе users
        - «users.write» — конкретное разрешение
    """

    @abstractmethod
    async def has_permission(self, user_id: Id, permission: str) -> bool:
        """
        Проверяет, есть ли у пользователя указанное разрешение.

        Аргументы:
            user_id: Идентификатор пользователя.
            permission: Требуемое разрешение (например «users.write»).

        Возвращает:
            True, если разрешение есть, иначе False.
        """

    @abstractmethod
    async def require_permission(self, user_id: Id, permission: str) -> None:
        """
        Проверяет разрешение и выбрасывает исключение при отсутствии.

        Аргументы:
            user_id: Идентификатор пользователя.
            permission: Требуемое разрешение.

        Raises:
            InsufficientPermissionsException: Если разрешение отсутствует.
        """
