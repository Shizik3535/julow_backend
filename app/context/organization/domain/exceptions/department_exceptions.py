from __future__ import annotations

from app.shared.domain.exceptions.business_rule_violation_exception import BusinessRuleViolationException


class DepartmentMemberAlreadyExistsException(BusinessRuleViolationException):
    """Участник уже состоит в подразделении."""

    def __init__(self, user_id: str = "", department_id: str = "") -> None:
        super().__init__(
            rule="UniqueDepartmentMember",
            message=f"Участник {user_id} уже состоит в подразделении {department_id}",
        )
