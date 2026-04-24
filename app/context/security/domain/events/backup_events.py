from __future__ import annotations

from dataclasses import dataclass

from app.shared.domain.base_domain_event import BaseDomainEvent
from app.context.security.domain.value_objects.backup_type import BackupType
from app.context.security.domain.value_objects.ip_rule_type import IpRuleType


@dataclass(frozen=True)
class BackupCreated(BaseDomainEvent):
    backup_id: str = ""
    backup_type: BackupType = BackupType.FULL
    size_bytes: int = 0


@dataclass(frozen=True)
class BackupRestored(BaseDomainEvent):
    backup_id: str = ""
    restored_by: str = ""


@dataclass(frozen=True)
class BackupFailed(BaseDomainEvent):
    backup_id: str = ""
    error_message: str = ""


@dataclass(frozen=True)
class EncryptionKeyRotated(BaseDomainEvent):
    encryption_config_id: str = ""


@dataclass(frozen=True)
class IpRuleAdded(BaseDomainEvent):
    rule_id: str = ""
    rule_type: IpRuleType = IpRuleType.WHITELIST
    ip_range: str = ""


@dataclass(frozen=True)
class IpRuleRemoved(BaseDomainEvent):
    rule_id: str = ""
