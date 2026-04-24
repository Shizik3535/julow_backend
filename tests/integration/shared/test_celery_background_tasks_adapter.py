"""Интеграционные тесты CeleryBackgroundTasksAdapter (реальный Celery + Redis)."""

import asyncio

import pytest
from celery import Celery

from app.shared.infrastructure.background_tasks.celery_background_tasks_adapter import (
    CeleryBackgroundTasksAdapter,
)


@pytest.mark.integration
class TestCeleryBackgroundTasksAdapter:
    """Тесты фоновых задач через Celery."""

    @pytest.fixture
    def adapter(self, celery_app: Celery) -> CeleryBackgroundTasksAdapter:
        return CeleryBackgroundTasksAdapter(celery_app=celery_app, use_celery=True)

    @pytest.fixture
    def adapter_asyncio(self, celery_app: Celery) -> CeleryBackgroundTasksAdapter:
        return CeleryBackgroundTasksAdapter(celery_app=celery_app, use_celery=False)

    # ── register_task ────────────────────────────────────────────────────

    def test_register_task(self, adapter: CeleryBackgroundTasksAdapter, celery_app: Celery) -> None:
        def sample_task(x: int) -> int:
            return x * 2

        adapter.register_task("test.sample_task", sample_task)
        assert "test.sample_task" in celery_app.tasks

    def test_register_multiple_tasks(self, adapter: CeleryBackgroundTasksAdapter, celery_app: Celery) -> None:
        def task_a() -> None: pass
        def task_b() -> None: pass
        adapter.register_task("test.task_a", task_a)
        adapter.register_task("test.task_b", task_b)
        assert "test.task_a" in celery_app.tasks
        assert "test.task_b" in celery_app.tasks

    # ── send_task ────────────────────────────────────────────────────────

    def test_send_task_returns_async_result(self, adapter: CeleryBackgroundTasksAdapter) -> None:
        def noop() -> None: pass
        adapter.register_task("test.noop", noop)
        result = adapter.send_task("test.noop")
        assert result is not None
        assert hasattr(result, "id")

    def test_send_task_with_args_and_kwargs(self, adapter: CeleryBackgroundTasksAdapter) -> None:
        captured: dict = {}

        def task_fn(a: int, b: int, key: str = "") -> None:
            captured["a"] = a
            captured["b"] = b
            captured["key"] = key

        adapter.register_task("test.with_args", task_fn)
        result = adapter.send_task("test.with_args", args=(1, 2), kwargs={"key": "val"})
        assert result is not None

    def test_send_task_with_countdown(self, adapter: CeleryBackgroundTasksAdapter) -> None:
        def countdown_task() -> None: pass
        adapter.register_task("test.countdown_task", countdown_task)
        result = adapter.send_task("test.countdown_task", countdown=10)
        assert result is not None

    def test_send_task_with_expires(self, adapter: CeleryBackgroundTasksAdapter) -> None:
        def expiring_task() -> None: pass
        adapter.register_task("test.expiring_task", expiring_task)
        result = adapter.send_task("test.expiring_task", expires=60)
        assert result is not None

    # ── run (Celery mode) ────────────────────────────────────────────────

    async def test_run_dispatches_via_celery(self, adapter: CeleryBackgroundTasksAdapter) -> None:
        async def my_coroutine(x: int) -> None:
            pass

        # send_task отправляет задачу — ошибок быть не должно
        await adapter.run(my_coroutine, 42)

    async def test_run_delayed_dispatches_via_celery(self, adapter: CeleryBackgroundTasksAdapter) -> None:
        async def my_coroutine() -> None:
            pass

        await adapter.run_delayed(my_coroutine, 5.0)

    # ── run (asyncio fallback) ───────────────────────────────────────────

    async def test_run_asyncio_fallback_executes_coroutine(
        self, adapter_asyncio: CeleryBackgroundTasksAdapter
    ) -> None:
        called = asyncio.Event()

        async def my_coroutine() -> None:
            called.set()

        await adapter_asyncio.run(my_coroutine)
        await asyncio.wait_for(called.wait(), timeout=2.0)
        assert called.is_set()

    async def test_run_asyncio_fallback_passes_args(
        self, adapter_asyncio: CeleryBackgroundTasksAdapter
    ) -> None:
        result: dict = {}
        done = asyncio.Event()

        async def my_coroutine(a: int, b: int) -> None:
            result["sum"] = a + b
            done.set()

        await adapter_asyncio.run(my_coroutine, 3, 7)
        await asyncio.wait_for(done.wait(), timeout=2.0)
        assert result["sum"] == 10

    async def test_run_delayed_asyncio_fallback(
        self, adapter_asyncio: CeleryBackgroundTasksAdapter
    ) -> None:
        called = asyncio.Event()

        async def my_coroutine() -> None:
            called.set()

        await adapter_asyncio.run_delayed(my_coroutine, 0.1)
        await asyncio.wait_for(called.wait(), timeout=3.0)
        assert called.is_set()
