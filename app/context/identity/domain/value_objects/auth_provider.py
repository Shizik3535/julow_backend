from __future__ import annotations

from enum import Enum


class AuthProvider(Enum):
    """
    Провайдер аутентификации.

    Значения:
        EMAIL_PASSWORD: Регистрация по email + пароль.
        OAUTH_GOOGLE: Google OAuth 2.0.
        OAUTH_GITHUB: GitHub OAuth 2.0.
        OAUTH_YANDEX: Яндекс OAuth 2.0.
        OAUTH_APPLE: Apple OAuth 2.0.
        SAML_SSO: SAML 2.0 SSO (настройка в отдельном BC, взаимодействие через ACL).
    """

    EMAIL_PASSWORD = "email_password"
    OAUTH_GOOGLE = "oauth_google"
    OAUTH_GITHUB = "oauth_github"
    OAUTH_YANDEX = "oauth_yandex"
    OAUTH_APPLE = "oauth_apple"
    SAML_SSO = "saml_sso"
