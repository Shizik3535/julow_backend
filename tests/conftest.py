"""
Глобальный conftest.py — общие фикстуры для всех типов тестов.

Этот файл загружается pytest автоматически для всех тестов.
Содержит фикстуры, используемые в unit, integration и e2e тестах.

Типы тестов:
    - unit: Без внешних зависимостей (моки, стабы)
    - integration: С реальными внешними сервисами (БД, Redis)
    - e2e: Полный HTTP-стек через TestClient

Запуск:
    pytest                    — все тесты
    pytest -m unit            — только unit
    pytest -m integration     — только integration
    pytest -m e2e             — только e2e
    pytest tests/unit         — по директории
"""

import os
import uuid

import pytest

from app.shared.domain.value_objects.id_vo import Id

# Принудительно устанавливаем тестовое окружение
os.environ["APP_ENV"] = "test"
os.environ["APP_DEBUG"] = "true"
os.environ["DB_NAME"] = "julow_test"


# ── Helpers ──────────────────────────────────────────────────────────────────


def make_id() -> Id:
    """Создать случайный Id."""
    return Id(value=uuid.uuid4())


# ── Fixtures ─────────────────────────────────────────────────────────────────


@pytest.fixture(scope="session")
def anyio_backend():
    """Используем asyncio как backend для anyio."""
    return "asyncio"


@pytest.fixture
def any_id() -> Id:
    """Случайный Id для тестов."""
    return make_id()
