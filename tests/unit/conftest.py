"""
Unit test conftest — фикстуры для unit-тестов.

Unit-тесты не зависят от внешних сервисов.
Все зависимости мокируются через pytest-mock.
"""

import pytest


@pytest.fixture(autouse=True)
def _unit_marker(request):
    """Проверяет, что тест помечен как unit."""
    if not request.node.get_closest_marker("unit"):
        pytest.skip("Test not marked as unit")
