from __future__ import annotations

from enum import Enum


class TimeReportGrouping(Enum):
    BY_USER = "by_user"
    BY_TEAM = "by_team"
    BY_PROJECT = "by_project"
    BY_TASK = "by_task"
    BY_CLIENT = "by_client"
    BY_CATEGORY = "by_category"
    BY_EPIC = "by_epic"
    BY_TAG = "by_tag"
