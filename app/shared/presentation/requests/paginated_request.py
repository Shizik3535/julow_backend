from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PaginatedRequest:
    """
    Базовый запрос с пагинацией.

    Атрибуты:
        page: Номер страницы (1-based).
        page_size: Размер страницы.
    """

    page: int = 1
    page_size: int = 20
