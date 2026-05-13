from __future__ import annotations

from enum import Enum


class ReportType(Enum):
    BY_PROJECT = "by_project"
    BY_TEAM = "by_team"
    BY_PERIOD = "by_period"
    BY_EFFORT = "by_effort"
    BY_PERFORMANCE = "by_performance"
    BURNDOWN = "burndown"
    VELOCITY = "velocity"
    CUMULATIVE_FLOW = "cumulative_flow"
    TIME_TRACKING = "time_tracking"
    BILLING_SUMMARY = "billing_summary"
    WORKLOAD = "workload"
    # Кросс-BC отчёты
    USER_ACTIVITY = "user_activity"
    LOGIN_ACTIVITY = "login_activity"
    COMMUNICATION_VOLUME = "communication_volume"
    STORAGE_USAGE = "storage_usage"
    NOTIFICATION_DELIVERY = "notification_delivery"
    AUDIT_SUMMARY = "audit_summary"
    SECURITY_INCIDENTS = "security_incidents"
    SUBSCRIPTION_SUMMARY = "subscription_summary"
    CUSTOM = "custom"
