"""Shared fixtures for Analytics unit tests."""
from __future__ import annotations

from app.context.analytics.domain.value_objects.data_source import DataSource

# DataSource, которые на момент создания реестра реально обслуживаются
# резолверами (см. ``infrastructure/query_execution/resolvers/*``).
# Используется в test_static_analytics_schema_adapter и
# test_system_dashboard_templates_seed для синхронизации проверок.
RESOLVER_SUPPORTED_DATA_SOURCES: set[DataSource] = {
    DataSource.TASKS,
    DataSource.TASK_STATUS_HISTORY,
    DataSource.SPRINTS,
    DataSource.SPRINT_BURNDOWN,
    DataSource.SPRINT_VELOCITY,
    DataSource.PROJECTS,
    DataSource.PROJECT_PROGRESS,
    DataSource.TIME_ENTRIES,
    DataSource.WORKLOAD,
    DataSource.WORKSPACES,
}
