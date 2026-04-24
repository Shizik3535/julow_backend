"""Unit-тесты для агрегата SSOIntegration (Organization BC)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.domain.aggregates.sso_integration import SSOIntegration
from app.context.organization.domain.value_objects.sso_provider import SSOProvider
from app.context.organization.domain.events.sso_integration_events import (
    SSOIntegrationAdded,
    SSOIntegrationUpdated,
    SSOIntegrationDeactivated,
)
from tests.factories import IdFactory


# ═══════════════════════════════════════════════════════════════════════════
# Создание
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestSSOIntegrationCreation:
    def test_create(self, new_sso: SSOIntegration) -> None:
        assert new_sso.provider == SSOProvider.SAML
        assert new_sso.entity_id == "https://idp.example.com"
        assert new_sso.is_active is True

    def test_create_emits_sso_integration_added(self, new_sso: SSOIntegration) -> None:
        events = new_sso.clear_domain_events()
        assert any(isinstance(e, SSOIntegrationAdded) for e in events)


# ═══════════════════════════════════════════════════════════════════════════
# Обновление
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestSSOIntegrationUpdate:
    def test_update_entity_id(self, sso: SSOIntegration) -> None:
        sso.update(entity_id="https://new-idp.example.com")
        assert sso.entity_id == "https://new-idp.example.com"

    def test_update_sso_url(self, sso: SSOIntegration) -> None:
        sso.update(sso_url="https://new-idp.example.com/sso")
        assert sso.sso_url == "https://new-idp.example.com/sso"

    def test_update_certificate(self, sso: SSOIntegration) -> None:
        sso.update(certificate="NEW_CERT")
        assert sso.certificate == "NEW_CERT"

    def test_update_group_mapping(self, sso: SSOIntegration) -> None:
        mapping = {"admin": "admins"}
        sso.update(group_mapping=mapping)
        assert sso.group_mapping == mapping

    def test_update_attribute_mapping(self, sso: SSOIntegration) -> None:
        mapping = {"email": "mail"}
        sso.update(attribute_mapping=mapping)
        assert sso.attribute_mapping == mapping

    def test_update_emits_event(self, sso: SSOIntegration) -> None:
        sso.update(entity_id="https://new.example.com")
        events = sso.clear_domain_events()
        assert any(isinstance(e, SSOIntegrationUpdated) for e in events)


# ═══════════════════════════════════════════════════════════════════════════
# Статус
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestSSOIntegrationStatus:
    def test_deactivate(self, sso: SSOIntegration) -> None:
        sso.deactivate()
        assert sso.is_active is False

    def test_deactivate_emits_event(self, sso: SSOIntegration) -> None:
        sso.deactivate()
        events = sso.clear_domain_events()
        assert any(isinstance(e, SSOIntegrationDeactivated) for e in events)

    def test_reactivate(self, sso: SSOIntegration) -> None:
        sso.deactivate()
        sso.clear_domain_events()
        sso.reactivate()
        assert sso.is_active is True
