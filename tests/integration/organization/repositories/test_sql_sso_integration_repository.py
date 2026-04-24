"""Интеграционные тесты SqlSSOIntegrationRepository (реальная PostgreSQL)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.domain.aggregates.sso_integration import SSOIntegration
from app.context.organization.domain.value_objects.sso_provider import SSOProvider
from app.context.organization.infrastructure.persistence.repositories.sql_sso_integration_repository import (
    SqlSSOIntegrationRepository,
)


@pytest.mark.integration
class TestSqlSSOIntegrationRepositoryAdd:
    """Тесты добавления."""

    async def test_add_and_get_by_id(
        self, sso_repo: SqlSSOIntegrationRepository, make_sso_integration
    ) -> None:
        sso = await make_sso_integration()
        found = await sso_repo.get_by_id(sso.id)
        assert found is not None
        assert found.id == sso.id


@pytest.mark.integration
class TestSqlSSOIntegrationRepositorySearch:
    """Тесты поиска."""

    async def test_get_by_org_id(
        self, sso_repo: SqlSSOIntegrationRepository, make_sso_integration, make_org
    ) -> None:
        org = await make_org()
        sso = await make_sso_integration(org_id=org.id)
        found = await sso_repo.get_by_org_id(org.id)
        assert len(found) >= 1
        assert any(s.id == sso.id for s in found)

    async def test_get_by_org_and_provider_found(
        self, sso_repo: SqlSSOIntegrationRepository, make_sso_integration, make_org
    ) -> None:
        org = await make_org()
        sso = await make_sso_integration(org_id=org.id, provider=SSOProvider.SAML)
        found = await sso_repo.get_by_org_and_provider(org.id, SSOProvider.SAML)
        assert found is not None
        assert found.id == sso.id

    async def test_get_by_org_and_provider_not_found(
        self, sso_repo: SqlSSOIntegrationRepository, make_org
    ) -> None:
        org = await make_org()
        found = await sso_repo.get_by_org_and_provider(org.id, SSOProvider.OIDC)
        assert found is None


@pytest.mark.integration
class TestSqlSSOIntegrationRepositoryUpdate:
    """Тесты обновления."""

    async def test_update_config(
        self, sso_repo: SqlSSOIntegrationRepository, make_sso_integration
    ) -> None:
        sso = await make_sso_integration()
        sso.update(entity_id="new-entity-id")
        sso.clear_domain_events()
        await sso_repo.update(sso)

        found = await sso_repo.get_by_id(sso.id)
        assert found is not None
        assert found.entity_id == "new-entity-id"

    async def test_update_deactivate(
        self, sso_repo: SqlSSOIntegrationRepository, make_sso_integration
    ) -> None:
        sso = await make_sso_integration()
        sso.deactivate()
        sso.clear_domain_events()
        await sso_repo.update(sso)

        found = await sso_repo.get_by_id(sso.id)
        assert found is not None
        assert found.is_active is False

    async def test_update_reactivate(
        self, sso_repo: SqlSSOIntegrationRepository, make_sso_integration
    ) -> None:
        sso = await make_sso_integration()
        sso.deactivate()
        sso.clear_domain_events()
        await sso_repo.update(sso)

        sso.reactivate()
        sso.clear_domain_events()
        await sso_repo.update(sso)

        found = await sso_repo.get_by_id(sso.id)
        assert found is not None
        assert found.is_active is True


@pytest.mark.integration
class TestSqlSSOIntegrationRepositoryDelete:
    """Тесты удаления."""

    async def test_delete(self, sso_repo: SqlSSOIntegrationRepository, make_sso_integration) -> None:
        sso = await make_sso_integration()
        await sso_repo.delete(sso.id)
        found = await sso_repo.get_by_id(sso.id)
        assert found is None
