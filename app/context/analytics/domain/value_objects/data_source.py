from __future__ import annotations

from enum import Enum


class DataSource(Enum):
    TASK_SUMMARY = "task_summary"
    TASK_STATUS = "task_status"
    TASK_PRIORITY = "task_priority"
    TIME_ENTRY = "time_entry"
    TIME_BY_USER = "time_by_user"
    TIME_BY_PROJECT = "time_by_project"
    SPRINT_VELOCITY = "sprint_velocity"
    SPRINT_BURNDOWN = "sprint_burndown"
    PROJECT_PROGRESS = "project_progress"
    WORKLOAD = "workload"
    BILLING = "billing"
    FILE_STORAGE = "file_storage"
    CUSTOM = "custom"
