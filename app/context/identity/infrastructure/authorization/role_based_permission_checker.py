from __future__ import annotations

from app.context.identity.application.exceptions.authorization_exceptions import (
    InsufficientPermissionsException,
)
from app.context.identity.application.ports.authorization.permission_checker_port import (
    PermissionCheckerPort,
)
from app.context.identity.domain.repositories.role_repository import RoleRepository
from app.context.identity.domain.repositories.user_repository import UserRepository
from app.shared.domain.value_objects.id_vo import Id


class RoleBasedPermissionChecker(PermissionCheckerPort):
    """
    Проверка разрешений на основе ролей пользователя.

    Загружает роли пользователя через UserRepository и RoleRepository,
    затем проверяет, покрывает ли хотя бы одна роль требуемое разрешение.

    Поддерживаемые wildcard-шаблоны:
        - «*» — полный доступ (покрывает всё)
        - «users.*» — покрывает любые «users.<sub>» разрешения
        - «users.write» — точное совпадение
    """

    def __init__(
        self,
        user_repo: UserRepository,
        role_repo: RoleRepository,
    ) -> None:
        self._user_repo = user_repo
        self._role_repo = role_repo

    async def has_permission(self, user_id: Id, permission: str) -> bool:
        user = await self._user_repo.get_by_id(user_id)
        if user is None:
            return False

        for role_id in user.role_ids:
            role = await self._role_repo.get_by_id(role_id)
            if role is None:
                continue
            if self._permission_grants(role.permissions, permission):
                return True

        return False

    async def require_permission(self, user_id: Id, permission: str) -> None:
        if not await self.has_permission(user_id, permission):
            raise InsufficientPermissionsException(permission)

    @staticmethod
    def _permission_grants(permissions: list[str], required: str) -> bool:
        """
        Проверяет, покрывает ли список разрешений требуемое.

        Правила:
            - «*» покрывает всё
            - «group.*» покрывает «group.anything»
            - точное совпадение строки
        """
        for perm in permissions:
            if perm == "*":
                return True
            if perm == required:
                return True
            if perm.endswith(".*"):
                prefix = perm[:-1]  # «users.»
                if required.startswith(prefix):
                    return True
        return False
