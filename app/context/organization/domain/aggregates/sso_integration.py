from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.shared.domain.base_aggregate import AggregateRoot
from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.domain.value_objects.sso_provider import SSOProvider
from app.context.organization.domain.value_objects.storage_config import StorageConfig
from app.context.organization.domain.events.sso_integration_events import (
    SSOIntegrationAdded,
    SSOIntegrationUpdated,
    SSOIntegrationDeactivated,
)


@dataclass
class SSOIntegration(AggregateRoot):
    """
    Корень агрегата SSO-интеграции (Organization BC).

    Связан с организацией через org_id. Уникальность по (org_id, provider).

    Атрибуты:
        org_id: Opaque ID организации.
        config: Конфигурация SSO.
        added_at: Время добавления.
        added_by: ID добавившего.
        is_active: Активна ли интеграция.
        created_at: Время создания.
        updated_at: Время последнего обновления.
    """

    org_id: Id = field(default_factory=Id.generate)
    provider: SSOProvider = SSOProvider.SAML
    entity_id: str = ""
    sso_url: str = ""
    certificate: str = ""
    is_active: bool = True
    group_mapping: dict[str, str] | None = None
    attribute_mapping: dict[str, str] | None = None
    added_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
    added_by: Id = field(default_factory=Id.generate)
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))

    # --- Фабричный метод ---

    @classmethod
    def create(
        cls,
        org_id: Id,
        provider: SSOProvider,
        entity_id: str,
        sso_url: str,
        certificate: str,
        added_by: Id,
        group_mapping: dict[str, str] | None = None,
        attribute_mapping: dict[str, str] | None = None,
    ) -> SSOIntegration:
        """Создаёт SSO-интеграцию."""
        integration = cls(
            org_id=org_id,
            provider=provider,
            entity_id=entity_id,
            sso_url=sso_url,
            certificate=certificate,
            added_by=added_by,
            group_mapping=group_mapping,
            attribute_mapping=attribute_mapping,
        )
        integration._register_event(
            SSOIntegrationAdded(org_id=str(org_id), provider=provider)
        )
        return integration

    # --- Бизнес-методы ---

    def update(
        self,
        entity_id: str | None = None,
        sso_url: str | None = None,
        certificate: str | None = None,
        group_mapping: dict[str, str] | None = None,
        attribute_mapping: dict[str, str] | None = None,
    ) -> None:
        """Обновляет конфигурацию SSO."""
        if entity_id is not None:
            self.entity_id = entity_id
        if sso_url is not None:
            self.sso_url = sso_url
        if certificate is not None:
            self.certificate = certificate
        if group_mapping is not None:
            self.group_mapping = group_mapping
        if attribute_mapping is not None:
            self.attribute_mapping = attribute_mapping
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            SSOIntegrationUpdated(org_id=str(self.org_id), provider=self.provider)
        )

    def deactivate(self) -> None:
        """Деактивирует SSO-интеграцию."""
        self.is_active = False
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            SSOIntegrationDeactivated(org_id=str(self.org_id), provider=self.provider)
        )

    def reactivate(self) -> None:
        """Реактивирует SSO-интеграцию."""
        self.is_active = True
        self.updated_at = datetime.now(tz=timezone.utc)
