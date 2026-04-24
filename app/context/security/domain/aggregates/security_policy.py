from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.shared.domain.base_aggregate import AggregateRoot
from app.shared.domain.value_objects.id_vo import Id
from app.context.security.domain.value_objects.data_residency import DataResidency
from app.context.security.domain.value_objects.password_policy_config import PasswordPolicyConfig
from app.context.security.domain.value_objects.session_policy_config import SessionPolicyConfig
from app.context.security.domain.value_objects.retention_policy_config import RetentionPolicyConfig
from app.context.security.domain.value_objects.compliance_standard import ComplianceStandard
from app.context.security.domain.value_objects.ip_rule_type import IpRuleType
from app.context.security.domain.entities.ip_rule import IpRule
from app.context.security.domain.entities.compliance_config import ComplianceConfig
from app.context.security.domain.entities.backup_schedule import BackupSchedule
from app.context.security.domain.entities.backup_record import BackupRecord
from app.context.security.domain.entities.encryption_config import EncryptionConfig
from app.context.security.domain.events.compliance_events import SecurityPolicyUpdated
from app.context.security.domain.events.backup_events import IpRuleAdded, IpRuleRemoved
from app.context.security.domain.exceptions.backup_exceptions import DuplicateIpRuleException


@dataclass
class SecurityPolicy(AggregateRoot):
    """Корень агрегата политики безопасности (Security BC)."""

    workspace_id: Id | None = None
    organization_id: Id | None = None
    password_policy: PasswordPolicyConfig = field(default_factory=PasswordPolicyConfig)
    session_policy: SessionPolicyConfig = field(default_factory=SessionPolicyConfig)
    ip_rules: list[IpRule] = field(default_factory=list)
    encryption_config: EncryptionConfig | None = None
    data_residency: DataResidency | None = None
    retention_policy: RetentionPolicyConfig = field(default_factory=RetentionPolicyConfig)
    compliance_configs: list[ComplianceConfig] = field(default_factory=list)
    backup_schedules: list[BackupSchedule] = field(default_factory=list)
    backup_records: list[BackupRecord] = field(default_factory=list)
    is_enforced: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))

    @classmethod
    def create(
        cls,
        password_policy: PasswordPolicyConfig,
        session_policy: SessionPolicyConfig,
        workspace_id: Id | None = None,
        organization_id: Id | None = None,
    ) -> SecurityPolicy:
        return cls(
            workspace_id=workspace_id,
            organization_id=organization_id,
            password_policy=password_policy,
            session_policy=session_policy,
        )

    def update_password_policy(self, config: PasswordPolicyConfig) -> None:
        self.password_policy = config
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(SecurityPolicyUpdated(policy_id=str(self.id), changed_fields=["password_policy"]))

    def update_session_policy(self, config: SessionPolicyConfig) -> None:
        self.session_policy = config
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(SecurityPolicyUpdated(policy_id=str(self.id), changed_fields=["session_policy"]))

    def add_ip_rule(self, ip_range: str, rule_type: IpRuleType, created_by: Id, description: str | None = None) -> None:
        if any(r.ip_range == ip_range and r.rule_type == rule_type for r in self.ip_rules):
            raise DuplicateIpRuleException(ip_range=ip_range)
        rule = IpRule(ip_range=ip_range, rule_type=rule_type, description=description, created_by=created_by)
        self.ip_rules.append(rule)
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(IpRuleAdded(rule_id=str(rule.id), rule_type=rule_type, ip_range=ip_range))

    def remove_ip_rule(self, rule_id: Id) -> None:
        rule = next((r for r in self.ip_rules if r.id == rule_id), None)
        if rule is not None:
            self.ip_rules.remove(rule)
            self.updated_at = datetime.now(tz=timezone.utc)
            self._register_event(IpRuleRemoved(rule_id=str(rule_id)))

    def set_encryption_config(self, config: EncryptionConfig) -> None:
        self.encryption_config = config
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(SecurityPolicyUpdated(policy_id=str(self.id), changed_fields=["encryption_config"]))

    def set_data_residency(self, residency: DataResidency) -> None:
        self.data_residency = residency
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(SecurityPolicyUpdated(policy_id=str(self.id), changed_fields=["data_residency"]))

    def update_retention_policy(self, config: RetentionPolicyConfig) -> None:
        self.retention_policy = config
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(SecurityPolicyUpdated(policy_id=str(self.id), changed_fields=["retention_policy"]))

    def add_compliance_config(self, config: ComplianceConfig) -> None:
        if any(c.standard == config.standard for c in self.compliance_configs):
            return
        self.compliance_configs.append(config)
        self.updated_at = datetime.now(tz=timezone.utc)

    def remove_compliance_config(self, standard: ComplianceStandard) -> None:
        self.compliance_configs = [c for c in self.compliance_configs if c.standard != standard]
        self.updated_at = datetime.now(tz=timezone.utc)

    def update_compliance_settings(self, standard: ComplianceStandard, settings: "ComplianceSettings") -> None:
        config = next((c for c in self.compliance_configs if c.standard == standard), None)
        if config is not None:
            config.settings = settings
        self.updated_at = datetime.now(tz=timezone.utc)

    def add_backup_schedule(self, schedule: BackupSchedule) -> None:
        if any(s.backup_type == schedule.backup_type for s in self.backup_schedules):
            return
        self.backup_schedules.append(schedule)
        self.updated_at = datetime.now(tz=timezone.utc)

    def remove_backup_schedule(self, schedule_id: Id) -> None:
        self.backup_schedules = [s for s in self.backup_schedules if s.id != schedule_id]
        self.updated_at = datetime.now(tz=timezone.utc)

    def record_backup(self, record: BackupRecord) -> None:
        self.backup_records.append(record)
        self.updated_at = datetime.now(tz=timezone.utc)

    def enforce(self) -> None:
        self.is_enforced = True
        self.updated_at = datetime.now(tz=timezone.utc)

    def unenforce(self) -> None:
        self.is_enforced = False
        self.updated_at = datetime.now(tz=timezone.utc)
