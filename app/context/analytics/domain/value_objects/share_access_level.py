from __future__ import annotations

from enum import Enum


class ShareAccessLevel(Enum):
    VIEW = "view"
    EDIT = "edit"
    ADMIN = "admin"
