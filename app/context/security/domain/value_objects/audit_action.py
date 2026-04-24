from __future__ import annotations

from enum import Enum


class AuditAction(Enum):
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    LOGIN_FAILED = "login_failed"
    EXPORT = "export"
    SHARE = "share"
    CONFIG_CHANGE = "config_change"
    MFA_ENABLED = "mfa_enabled"
    MFA_DISABLED = "mfa_disabled"
    PASSWORD_CHANGE = "password_change"
    ROLE_CHANGE = "role_change"
    API_KEY_CREATED = "api_key_created"
    API_KEY_REVOKED = "api_key_revoked"
    PERMISSION_CHANGE = "permission_change"
    DATA_EXPORT = "data_export"
    DATA_DELETE = "data_delete"
