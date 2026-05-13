from app.context.analytics.application.commands.add_widget import (
    AddWidgetCommand,
    AddWidgetHandler,
)
from app.context.analytics.application.commands.create_custom_template import (
    CreateCustomTemplateCommand,
    CreateCustomTemplateHandler,
)
from app.context.analytics.application.commands.create_dashboard import (
    CreateDashboardCommand,
    CreateDashboardHandler,
)
from app.context.analytics.application.commands.create_dashboard_from_template import (
    CreateDashboardFromTemplateCommand,
    CreateDashboardFromTemplateHandler,
)
from app.context.analytics.application.commands.create_report import (
    CreateReportCommand,
    CreateReportHandler,
)
from app.context.analytics.application.commands.delete_dashboard import (
    DeleteDashboardCommand,
    DeleteDashboardHandler,
)
from app.context.analytics.application.commands.delete_report import (
    DeleteReportCommand,
    DeleteReportHandler,
)
from app.context.analytics.application.commands.delete_template import (
    DeleteTemplateCommand,
    DeleteTemplateHandler,
)
from app.context.analytics.application.commands.generate_report import (
    GenerateReportCommand,
    GenerateReportHandler,
)
from app.context.analytics.application.commands.remove_report_schedule import (
    DeactivateReportScheduleCommand,
    DeactivateReportScheduleHandler,
    RemoveReportScheduleCommand,
    RemoveReportScheduleHandler,
)
from app.context.analytics.application.commands.remove_widget import (
    RemoveWidgetCommand,
    RemoveWidgetHandler,
)
from app.context.analytics.application.commands.send_report_now import (
    SendReportNowCommand,
    SendReportNowHandler,
)
from app.context.analytics.application.commands.set_dashboard_auto_refresh import (
    SetDashboardAutoRefreshCommand,
    SetDashboardAutoRefreshHandler,
)
from app.context.analytics.application.commands.set_default_dashboard import (
    SetDefaultDashboardCommand,
    SetDefaultDashboardHandler,
)
from app.context.analytics.application.commands.set_report_schedule import (
    SetReportScheduleCommand,
    SetReportScheduleHandler,
)
from app.context.analytics.application.commands.share_dashboard import (
    ShareDashboardCommand,
    ShareDashboardHandler,
    UnshareDashboardCommand,
    UnshareDashboardHandler,
)
from app.context.analytics.application.commands.share_report import (
    ShareReportCommand,
    ShareReportHandler,
    UnshareReportCommand,
    UnshareReportHandler,
)
from app.context.analytics.application.commands.update_dashboard import (
    UpdateDashboardCommand,
    UpdateDashboardHandler,
)
from app.context.analytics.application.commands.update_dashboard_layout import (
    UpdateDashboardLayoutCommand,
    UpdateDashboardLayoutHandler,
)
from app.context.analytics.application.commands.update_report import (
    UpdateReportCommand,
    UpdateReportHandler,
)
from app.context.analytics.application.commands.update_widget import (
    UpdateWidgetCommand,
    UpdateWidgetHandler,
)

__all__ = [
    "AddWidgetCommand",
    "AddWidgetHandler",
    "CreateCustomTemplateCommand",
    "CreateCustomTemplateHandler",
    "CreateDashboardCommand",
    "CreateDashboardFromTemplateCommand",
    "CreateDashboardFromTemplateHandler",
    "CreateDashboardHandler",
    "CreateReportCommand",
    "CreateReportHandler",
    "DeactivateReportScheduleCommand",
    "DeactivateReportScheduleHandler",
    "DeleteDashboardCommand",
    "DeleteDashboardHandler",
    "DeleteReportCommand",
    "DeleteReportHandler",
    "DeleteTemplateCommand",
    "DeleteTemplateHandler",
    "GenerateReportCommand",
    "GenerateReportHandler",
    "RemoveReportScheduleCommand",
    "RemoveReportScheduleHandler",
    "RemoveWidgetCommand",
    "RemoveWidgetHandler",
    "SendReportNowCommand",
    "SendReportNowHandler",
    "SetDashboardAutoRefreshCommand",
    "SetDashboardAutoRefreshHandler",
    "SetDefaultDashboardCommand",
    "SetDefaultDashboardHandler",
    "SetReportScheduleCommand",
    "SetReportScheduleHandler",
    "ShareDashboardCommand",
    "ShareDashboardHandler",
    "ShareReportCommand",
    "ShareReportHandler",
    "UnshareDashboardCommand",
    "UnshareDashboardHandler",
    "UnshareReportCommand",
    "UnshareReportHandler",
    "UpdateDashboardCommand",
    "UpdateDashboardHandler",
    "UpdateDashboardLayoutCommand",
    "UpdateDashboardLayoutHandler",
    "UpdateReportCommand",
    "UpdateReportHandler",
    "UpdateWidgetCommand",
    "UpdateWidgetHandler",
]
