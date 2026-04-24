from __future__ import annotations

from app.shared.domain.exceptions import EntityNotFoundException


class AuditLogNotFoundException(EntityNotFoundException):
    def __init__(self, id: object) -> None:
        super().__init__(entity_type="AuditLog", id=id)
