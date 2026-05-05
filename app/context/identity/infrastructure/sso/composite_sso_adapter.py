from __future__ import annotations

from app.context.identity.application.ports.sso.sso_port import SSOPort, SSOUserInfo
from app.context.identity.infrastructure.sso.exceptions import SSOAuthenticationException


class CompositeSSOAdapter(SSOPort):
    """
    Composite SSO-адаптер — роутер по типу провайдера.

    Делегирует вызовы конкретному адаптеру (SAML, OIDC, LDAP)
    в зависимости от параметра provider.
    """

    def __init__(self, adapters: list[SSOPort]) -> None:
        self._adapters = adapters

    def _get_adapter(self, provider: str) -> SSOPort:
        """Найти адаптер, поддерживающий указанный протокол."""
        for adapter in self._adapters:
            if adapter.supports_protocol(provider):
                return adapter
        raise SSOAuthenticationException(f"Unsupported SSO provider: {provider}")

    def build_auth_request(
        self,
        provider: str,
        entity_id: str,
        sso_url: str,
        certificate: str,
        callback_url: str,
        attribute_mapping: dict[str, str] | None = None,
    ) -> str:
        adapter = self._get_adapter(provider)
        return adapter.build_auth_request(
            provider=provider,
            entity_id=entity_id,
            sso_url=sso_url,
            certificate=certificate,
            callback_url=callback_url,
            attribute_mapping=attribute_mapping,
        )

    async def process_response(
        self,
        provider: str,
        entity_id: str,
        sso_url: str,
        certificate: str,
        callback_url: str,
        response_data: dict,
        attribute_mapping: dict[str, str] | None = None,
    ) -> SSOUserInfo:
        adapter = self._get_adapter(provider)
        return await adapter.process_response(
            provider=provider,
            entity_id=entity_id,
            sso_url=sso_url,
            certificate=certificate,
            callback_url=callback_url,
            response_data=response_data,
            attribute_mapping=attribute_mapping,
        )

    def supports_protocol(self, provider: str) -> bool:
        return any(a.supports_protocol(provider) for a in self._adapters)
