from __future__ import annotations

from enum import Enum


class SecurityEventType(Enum):
    BRUTE_FORCE = "brute_force"
    SUSPICIOUS_LOGIN = "suspicious_login"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    DATA_EXFILTRATION = "data_exfiltration"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    CONFIG_DRIFT = "config_drift"
    COMPLIANCE_VIOLATION = "compliance_violation"
    ENCRYPTION_FAILURE = "encryption_failure"
    BACKUP_FAILURE = "backup_failure"
    OTHER = "other"
