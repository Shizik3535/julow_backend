"""analytics_initial

Создаёт таблицы Analytics BC:
- analytics_dashboards, analytics_dashboard_widgets, analytics_dashboard_shares
- analytics_dashboard_templates
- analytics_reports, analytics_report_shares
- analytics_report_jobs

Revision ID: e7f8a9b0c1d2
Revises: d5e6f7a8b9c0
Create Date: 2026-05-14 02:13:00.000000+00:00
"""
from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op


revision: str = "e7f8a9b0c1d2"
down_revision: str | Sequence[str] | None = "d5e6f7a8b9c0"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""

    # --- analytics_dashboards ---
    op.create_table(
        "analytics_dashboards",
        sa.Column("owner_id", sa.Uuid(), nullable=False),
        sa.Column("workspace_id", sa.Uuid(), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "is_auto_refresh",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column("refresh_interval_seconds", sa.Integer(), nullable=True),
        sa.Column(
            "is_default",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_analytics_dashboards_workspace",
        "analytics_dashboards",
        ["workspace_id"],
    )
    op.create_index(
        "ix_analytics_dashboards_owner",
        "analytics_dashboards",
        ["owner_id"],
    )
    op.create_index(
        "ix_analytics_dashboards_workspace_default",
        "analytics_dashboards",
        ["workspace_id", "is_default"],
    )

    # --- analytics_dashboard_widgets ---
    op.create_table(
        "analytics_dashboard_widgets",
        sa.Column("dashboard_id", sa.Uuid(), nullable=False),
        sa.Column(
            "title",
            sa.String(length=255),
            nullable=False,
            server_default="",
        ),
        sa.Column("widget_type", sa.String(length=32), nullable=False),
        sa.Column("config", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("size_cols", sa.Integer(), nullable=False, server_default="6"),
        sa.Column("size_rows", sa.Integer(), nullable=False, server_default="4"),
        sa.Column("position_row", sa.Integer(), nullable=True),
        sa.Column("position_col", sa.Integer(), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["dashboard_id"],
            ["analytics_dashboards.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_analytics_dashboard_widgets_dashboard",
        "analytics_dashboard_widgets",
        ["dashboard_id"],
    )

    # --- analytics_dashboard_shares ---
    op.create_table(
        "analytics_dashboard_shares",
        sa.Column("dashboard_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("access_level", sa.String(length=16), nullable=False),
        sa.Column("shared_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["dashboard_id"],
            ["analytics_dashboards.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_analytics_dashboard_shares_dashboard",
        "analytics_dashboard_shares",
        ["dashboard_id"],
    )
    op.create_index(
        "ix_analytics_dashboard_shares_user",
        "analytics_dashboard_shares",
        ["user_id"],
    )

    # --- analytics_dashboard_templates ---
    op.create_table(
        "analytics_dashboard_templates",
        sa.Column("workspace_id", sa.Uuid(), nullable=True),
        sa.Column(
            "name",
            sa.String(length=255),
            nullable=False,
            server_default="",
        ),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "widget_configs",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column(
            "is_system",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column(
            "is_deleted",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        # Зеркалирует DDD-инвариант DashboardTemplate.__post_init__:
        # системный шаблон глобален (workspace_id IS NULL),
        # пользовательский — обязательно привязан к workspace.
        # Без этого CHECK раздельный путь записи (raw SQL, фикстуры) мог бы
        # породить строку, на которой to_domain() падает ValidationException.
        sa.CheckConstraint(
            "(is_system = true AND workspace_id IS NULL)"
            " OR (is_system = false AND workspace_id IS NOT NULL)",
            name="ck_analytics_dashboard_templates_workspace_scope",
        ),
    )
    op.create_index(
        "ix_analytics_dashboard_templates_system",
        "analytics_dashboard_templates",
        ["is_system"],
    )
    op.create_index(
        "ix_analytics_dashboard_templates_name",
        "analytics_dashboard_templates",
        ["name"],
    )
    op.create_index(
        "ix_analytics_dashboard_templates_workspace",
        "analytics_dashboard_templates",
        ["workspace_id"],
    )

    # --- analytics_reports ---
    op.create_table(
        "analytics_reports",
        sa.Column("owner_id", sa.Uuid(), nullable=False),
        sa.Column("workspace_id", sa.Uuid(), nullable=True),
        sa.Column(
            "name",
            sa.String(length=255),
            nullable=False,
            server_default="",
        ),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("report_type", sa.String(length=64), nullable=False),
        sa.Column(
            "query",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column("query_data_source", sa.String(length=64), nullable=False),
        sa.Column("query_bounded_context", sa.String(length=32), nullable=False),
        sa.Column("schedule_frequency", sa.String(length=16), nullable=True),
        sa.Column(
            "schedule_recipients",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column(
            "schedule_is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column("schedule_next_run_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("schedule_last_run_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_generated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_export_format", sa.String(length=16), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_analytics_reports_workspace",
        "analytics_reports",
        ["workspace_id"],
    )
    op.create_index(
        "ix_analytics_reports_owner",
        "analytics_reports",
        ["owner_id"],
    )
    op.create_index(
        "ix_analytics_reports_report_type",
        "analytics_reports",
        ["report_type"],
    )
    op.create_index(
        "ix_analytics_reports_query_data_source",
        "analytics_reports",
        ["query_data_source"],
    )
    op.create_index(
        "ix_analytics_reports_query_bounded_context",
        "analytics_reports",
        ["query_bounded_context"],
    )
    op.create_index(
        "ix_analytics_reports_workspace_type",
        "analytics_reports",
        ["workspace_id", "report_type"],
    )
    op.create_index(
        "ix_analytics_reports_schedule_active",
        "analytics_reports",
        ["schedule_is_active", "schedule_next_run_at"],
    )

    # --- analytics_report_shares ---
    op.create_table(
        "analytics_report_shares",
        sa.Column("report_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("access_level", sa.String(length=16), nullable=False),
        sa.Column("shared_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["report_id"],
            ["analytics_reports.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_analytics_report_shares_report",
        "analytics_report_shares",
        ["report_id"],
    )
    op.create_index(
        "ix_analytics_report_shares_user",
        "analytics_report_shares",
        ["user_id"],
    )

    # --- analytics_report_jobs ---
    op.create_table(
        "analytics_report_jobs",
        sa.Column("report_id", sa.Uuid(), nullable=True),
        sa.Column("workspace_id", sa.Uuid(), nullable=False),
        sa.Column("report_type", sa.String(length=64), nullable=False),
        sa.Column(
            "query",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column("format", sa.String(length=16), nullable=False),
        sa.Column(
            "status",
            sa.String(length=16),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("download_url", sa.String(length=1024), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("requested_by", sa.Uuid(), nullable=False),
        sa.Column("requested_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("estimated_seconds", sa.Integer(), nullable=True),
        sa.Column("scheduled_report_id", sa.Uuid(), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_analytics_report_jobs_report",
        "analytics_report_jobs",
        ["report_id"],
    )
    op.create_index(
        "ix_analytics_report_jobs_workspace",
        "analytics_report_jobs",
        ["workspace_id"],
    )
    op.create_index(
        "ix_analytics_report_jobs_status",
        "analytics_report_jobs",
        ["status"],
    )
    op.create_index(
        "ix_analytics_report_jobs_requested_by",
        "analytics_report_jobs",
        ["requested_by"],
    )
    op.create_index(
        "ix_analytics_report_jobs_scheduled_report",
        "analytics_report_jobs",
        ["scheduled_report_id"],
    )


def downgrade() -> None:
    """Downgrade schema."""
    # analytics_report_jobs
    op.drop_index(
        "ix_analytics_report_jobs_scheduled_report",
        table_name="analytics_report_jobs",
    )
    op.drop_index(
        "ix_analytics_report_jobs_requested_by",
        table_name="analytics_report_jobs",
    )
    op.drop_index(
        "ix_analytics_report_jobs_status",
        table_name="analytics_report_jobs",
    )
    op.drop_index(
        "ix_analytics_report_jobs_workspace",
        table_name="analytics_report_jobs",
    )
    op.drop_index(
        "ix_analytics_report_jobs_report",
        table_name="analytics_report_jobs",
    )
    op.drop_table("analytics_report_jobs")

    # analytics_report_shares
    op.drop_index(
        "ix_analytics_report_shares_user",
        table_name="analytics_report_shares",
    )
    op.drop_index(
        "ix_analytics_report_shares_report",
        table_name="analytics_report_shares",
    )
    op.drop_table("analytics_report_shares")

    # analytics_reports
    op.drop_index(
        "ix_analytics_reports_schedule_active",
        table_name="analytics_reports",
    )
    op.drop_index(
        "ix_analytics_reports_workspace_type",
        table_name="analytics_reports",
    )
    op.drop_index(
        "ix_analytics_reports_query_bounded_context",
        table_name="analytics_reports",
    )
    op.drop_index(
        "ix_analytics_reports_query_data_source",
        table_name="analytics_reports",
    )
    op.drop_index(
        "ix_analytics_reports_report_type",
        table_name="analytics_reports",
    )
    op.drop_index(
        "ix_analytics_reports_owner",
        table_name="analytics_reports",
    )
    op.drop_index(
        "ix_analytics_reports_workspace",
        table_name="analytics_reports",
    )
    op.drop_table("analytics_reports")

    # analytics_dashboard_templates
    op.drop_index(
        "ix_analytics_dashboard_templates_workspace",
        table_name="analytics_dashboard_templates",
    )
    op.drop_index(
        "ix_analytics_dashboard_templates_name",
        table_name="analytics_dashboard_templates",
    )
    op.drop_index(
        "ix_analytics_dashboard_templates_system",
        table_name="analytics_dashboard_templates",
    )
    op.drop_table("analytics_dashboard_templates")

    # analytics_dashboard_shares
    op.drop_index(
        "ix_analytics_dashboard_shares_user",
        table_name="analytics_dashboard_shares",
    )
    op.drop_index(
        "ix_analytics_dashboard_shares_dashboard",
        table_name="analytics_dashboard_shares",
    )
    op.drop_table("analytics_dashboard_shares")

    # analytics_dashboard_widgets
    op.drop_index(
        "ix_analytics_dashboard_widgets_dashboard",
        table_name="analytics_dashboard_widgets",
    )
    op.drop_table("analytics_dashboard_widgets")

    # analytics_dashboards
    op.drop_index(
        "ix_analytics_dashboards_workspace_default",
        table_name="analytics_dashboards",
    )
    op.drop_index(
        "ix_analytics_dashboards_owner",
        table_name="analytics_dashboards",
    )
    op.drop_index(
        "ix_analytics_dashboards_workspace",
        table_name="analytics_dashboards",
    )
    op.drop_table("analytics_dashboards")
