from __future__ import annotations

from app.context.profile.application.ports.navigation.start_page_registry_port import (
    StartPageRegistryPort,
)

_REGISTERED_PAGES: frozenset[str] = frozenset({
    "my_tasks",
    "dashboard",
    "inbox",
    "calendar",
    "reports",
    "team",
})


class StartPageRegistryAdapter(StartPageRegistryPort):
    """
    Реализация StartPageRegistryPort.

    Статический реестр зарегистрированных стартовых страниц.
    Страницы определены в спецификации Profile BC (§13.1).
    При расширении списка — добавить значение в _REGISTERED_PAGES.
    """

    async def is_registered(self, page: str) -> bool:
        return page in _REGISTERED_PAGES

    async def get_registered_pages(self) -> list[str]:
        return sorted(_REGISTERED_PAGES)
