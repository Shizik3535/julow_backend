from __future__ import annotations

from enum import Enum


class OrgRoleScope(Enum):
    """
    Область действия роли организации.

    Значения:
        ORG: Роль действует на всю организацию
        DEPARTMENT: Роль действует на подразделение
        TEAM: Роль действует на команду
    """

    ORG = "org"
    DEPARTMENT = "department"
    TEAM = "team"
