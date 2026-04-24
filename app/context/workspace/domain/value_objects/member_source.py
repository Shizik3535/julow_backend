from __future__ import annotations

from enum import Enum


class MemberSource(Enum):
    """
    Источник участника workspace.

    Значения:
        DIRECT: Прямое добавление
        ORGANIZATION: Из организации (ACL)
        PARENT_WORKSPACE: Унаследован из родительского workspace
        INVITATION_LINK: По ссылке-приглашению
    """

    DIRECT = "direct"
    ORGANIZATION = "organization"
    PARENT_WORKSPACE = "parent_workspace"
    INVITATION_LINK = "invitation_link"
