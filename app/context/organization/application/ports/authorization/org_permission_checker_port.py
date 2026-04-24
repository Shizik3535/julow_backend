from __future__ import annotations

from abc import ABC, abstractmethod

from app.shared.domain.value_objects.id_vo import Id


class OrgPermissionCheckerPort(ABC):
    """
    Порт проверки разрешений пользователя в контексте организации (Organization BC).

    Проверяет, обладает ли пользователь указанным разрешением
    на основе его орг-роли. Поддерживает wildcard-разрешения:
        - «org.*» — полный доступ в организации
        - «members.*» — все разрешения в группе members
        - «members.write» — конкретное разрешение
    """

    @abstractmethod
    async def has_permission(self, user_id: Id, org_id: Id, permission: str) -> bool:
        """
        Проверяет, есть ли у пользователя указанное разрешение в организации.

        Аргументы:
            user_id: Идентификатор пользователя.
            org_id: Идентификатор организации.
            permission: Требуемое разрешение (например «members.write»).

        Возвращает:
            True, если разрешение есть, иначе False.
        """

    @abstractmethod
    async def require_permission(self, user_id: Id, org_id: Id, permission: str) -> None:
        """
        Проверяет разрешение и выбрасывает исключение при отсутствии.

        Аргументы:
            user_id: Идентификатор пользователя.
            org_id: Идентификатор организации.
            permission: Требуемое разрешение.

        Raises:
            InsufficientOrgPermissionsException: Если разрешение отсутствует.
        """
