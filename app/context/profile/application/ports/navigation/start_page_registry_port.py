from __future__ import annotations

from abc import ABC, abstractmethod


class StartPageRegistryPort(ABC):
    """
    BC-специфичный порт: реестр зарегистрированных стартовых страниц.

    Используется на app-слое для валидации StartPage —
    проверяет, что идентификатор страницы существует в системе.

    Реализация — адаптер в infrastructure-слое Profile BC
    (например, читает конфигурацию из БД или статического реестра).
    """

    @abstractmethod
    async def is_registered(self, page: str) -> bool:
        """
        Проверить, зарегистрирована ли стартовая страница.

        Аргументы:
            page: Идентификатор страницы (например "dashboard", "my_tasks").

        Возвращает:
            True, если страница зарегистрирована в системе.
        """

    @abstractmethod
    async def get_registered_pages(self) -> list[str]:
        """
        Получить список всех зарегистрированных стартовых страниц.

        Возвращает:
            Список идентификаторов страниц.
        """
