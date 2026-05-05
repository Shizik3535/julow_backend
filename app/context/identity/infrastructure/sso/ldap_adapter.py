from __future__ import annotations

from app.context.identity.application.ports.sso.sso_port import SSOPort, SSOUserInfo


class LdapSSOAdapter(SSOPort):
    """
    SSO-адаптер для LDAP.

    LDAP не имеет redirect-based flow. Вместо этого:
    - build_auth_request возвращает маркер 'ldap_direct_bind'
    - process_response выполняет LDAP bind + search
    """

    # Маркер, указывающий, что LDAP требует прямого ввода credentials
    LDAP_DIRECT_MARKER = "__ldap_direct_bind__"

    def build_auth_request(
        self,
        provider: str,
        entity_id: str,
        sso_url: str,
        certificate: str,
        callback_url: str,
        attribute_mapping: dict[str, str] | None = None,
    ) -> str:
        # LDAP не поддерживает redirect-flow, возвращаем маркер
        return self.LDAP_DIRECT_MARKER

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
        """
        Выполнить LDAP bind и поиск пользователя.

        response_data должен содержать:
            - username: имя пользователя (DN или sAMAccountName)
            - password: пароль для LDAP bind
        """
        import ldap3
        from ldap3 import Server, Connection, ALL, SUBTREE
        from ldap3.core.exceptions import LDAPBindError, LDAPException

        username = response_data.get("username", "")
        password = response_data.get("password", "")

        if not username or not password:
            from app.context.identity.infrastructure.sso.exceptions import SSOAuthenticationException
            raise SSOAuthenticationException("LDAP requires username and password")

        mapping = attribute_mapping or {}
        base_dn = mapping.get("base_dn", entity_id)
        user_filter = mapping.get("user_filter", "(sAMAccountName={username})")
        email_attr = mapping.get("email", "mail")
        name_attr = mapping.get("display_name", "displayName")
        groups_attr = mapping.get("groups", "memberOf")
        id_attr = mapping.get("id", "objectGUID")

        # Формируем user DN для bind
        bind_dn = username if "=" in username else f"uid={username},{base_dn}"

        try:
            server = Server(sso_url, get_info=ALL, use_ssl=sso_url.startswith("ldaps"))
            conn = Connection(server, user=bind_dn, password=password, auto_bind=True)
        except LDAPBindError:
            from app.context.identity.infrastructure.sso.exceptions import SSOAuthenticationException
            raise SSOAuthenticationException("LDAP bind failed: invalid credentials")
        except LDAPException as e:
            from app.context.identity.infrastructure.sso.exceptions import SSOAuthenticationException
            raise SSOAuthenticationException(f"LDAP connection error: {e}")

        try:
            # Поиск пользователя
            search_filter = user_filter.replace("{username}", username.split(",")[0].split("=")[-1])
            conn.search(
                search_base=base_dn,
                search_filter=search_filter,
                search_scope=SUBTREE,
                attributes=[email_attr, name_attr, groups_attr, id_attr],
            )

            if not conn.entries:
                from app.context.identity.infrastructure.sso.exceptions import SSOAuthenticationException
                raise SSOAuthenticationException("LDAP user not found after bind")

            entry = conn.entries[0]
            email = str(entry[email_attr]) if email_attr in entry else ""
            display_name = str(entry[name_attr]) if name_attr in entry else None
            groups = [str(g) for g in entry[groups_attr]] if groups_attr in entry else []
            provider_user_id = str(entry[id_attr]) if id_attr in entry else username

            return SSOUserInfo(
                provider_user_id=provider_user_id,
                email=email,
                display_name=display_name,
                groups=groups,
                attributes={"dn": str(entry.entry_dn)},
            )
        finally:
            conn.unbind()

    def supports_protocol(self, provider: str) -> bool:
        return provider == "ldap"
