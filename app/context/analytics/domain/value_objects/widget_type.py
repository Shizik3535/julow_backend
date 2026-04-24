from __future__ import annotations

from enum import Enum


class WidgetType(Enum):
    PIE_CHART = "pie_chart"
    LINE_CHART = "line_chart"
    BAR_CHART = "bar_chart"
    NUMBER = "number"
    TABLE = "table"
    LIST = "list"
    BURNDOWN_CHART = "burndown_chart"
    CUMULATIVE_FLOW = "cumulative_flow"
    HEATMAP = "heatmap"
    GAUGE = "gauge"
    KANBAN_BOARD = "kanban_board"
    SCATTER_PLOT = "scatter_plot"
    HISTOGRAM = "histogram"
