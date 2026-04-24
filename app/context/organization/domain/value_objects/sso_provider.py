from __future__ import annotations

from enum import Enum


class SSOProvider(Enum):
    """
    Провайдер SSO.

    Значения:
        SAML: SAML 2.0
        OIDC: OpenID Connect
        LDAP: LDAP
    """

    SAML = "saml"
    OIDC = "oidc"
    LDAP = "ldap"
