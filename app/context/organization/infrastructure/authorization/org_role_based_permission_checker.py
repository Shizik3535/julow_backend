from __future__ import annotations

from app.context.organization.application.exceptions.authorization_exceptions import (
    InsufficientOrgPermissionsException,
)
from app.context.organization.application.ports.authorization.org_permission_checker_port import (
    OrgPermissionCheckerPort,
)
from app.context.organization.domain.repositories.org_membership_repository import OrgMembershipRepository
from app.context.organization.domain.repositories.org_role_repository import OrgRoleRepository
from app.shared.domain.value_objects.id_vo import Id


class OrgRoleBasedPermissionChecker(OrgPermissionCheckerPort):
    """
    Проверка разрешений на основе орг-роли пользователя.

    Загружает участника через OrgMembershipRepository и его роль
    через OrgRoleRepository, затем проверяет, покрывает ли роль
    требуемое разрешение.

    Поддерживаемые wildcard-шаблоны:
        - «org.*» — полный доступ в организации (покрывает всё)
        - «members.*» — покрывает любые «members.<sub>» разрешения
        - «members.write» — точное совпадение
    """

    def __init__(
        self,
        membership_repo: OrgMembershipRepository,
        org_role_repo: OrgRoleRepository,
    ) -> None:
        self._membership_repo = membership_repo
        self._org_role_repo = org_role_repo

    async def has_permission(self, user_id: Id, org_id: Id, permission: str) -> bool:
        member = await self._membership_repo.get_member_by_org_and_user(org_id, user_id)
        if member is None or not member.is_active:
            return False

        role = await self._org_role_repo.get_by_id(member.role_id)
        if role is None:
            return False

        return self._permission_grants(role.permissions, permission)

    async def require_permission(self, user_id: Id, org_id: Id, permission: str) -> None:
        if not await self.has_permission(user_id, org_id, permission):
            raise InsufficientOrgPermissionsException(permission, str(org_id))

    @staticmethod
    def _permission_grants(permissions: list[str], required: str) -> bool:
        """
        Проверяет, покрывает ли список разрешений требуемое.

        Правила:
            - «org.*» покрывает всё
            - «group.*» покрывает «group.anything»
            - точное совпадение строки
        """
        for perm in permissions:
            if perm == "org.*":
                return True
            if perm == required:
                return True
            if perm.endswith(".*"):
                prefix = perm[:-1]  # «group.»
                if required.startswith(prefix):
                    return True
        return False
