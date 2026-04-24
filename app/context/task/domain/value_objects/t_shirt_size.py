from __future__ import annotations

from enum import Enum


class TShirtSize(Enum):
    """
    T-shirt размер для оценки усилия.

    Значения:
        XS: Extra Small
        S: Small
        M: Medium
        L: Large
        XL: Extra Large
    """

    XS = "xs"
    S = "s"
    M = "m"
    L = "l"
    XL = "xl"
