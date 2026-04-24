from __future__ import annotations

from dataclasses import dataclass

from app.shared.domain.base_domain_event import BaseDomainEvent


@dataclass(frozen=True)
class RetroTemplateCreated(BaseDomainEvent):
    """Шаблон ретроспективы создан."""

    template_name: str = ""


@dataclass(frozen=True)
class RetroTemplateUpdated(BaseDomainEvent):
    """Шаблон ретроспективы обновлён."""

    template_name: str = ""


@dataclass(frozen=True)
class RetroTemplateDeleted(BaseDomainEvent):
    """Шаблон ретроспективы удалён."""

    template_name: str = ""
