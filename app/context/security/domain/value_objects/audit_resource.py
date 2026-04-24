from __future__ import annotations

from enum import Enum


class AuditResource(Enum):
    USER = "user"
    ORGANIZATION = "organization"
    WORKSPACE = "workspace"
    PROJECT = "project"
    TASK = "task"
    FILE = "file"
    COMMENT = "comment"
    CHAT = "chat"
    MEETING = "meeting"
    TIME_ENTRY = "time_entry"
    INVOICE = "invoice"
    SUBSCRIPTION = "subscription"
    PLAN = "plan"
    SYSTEM = "system"
    API_KEY = "api_key"
    SECURITY_POLICY = "security_policy"
