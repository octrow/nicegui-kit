"""nicegui_kit.run_pool: слоты, очередь, отмена, история.

Каждый асинхронный сценарий заворачивается в `asyncio.run(...)`. Спавнер
инжектируется (`asyncio.create_task` вместо `background_tasks.create`, которому
нужен запущенный NiceGUI), подпроцессы — дешёвые `python -c ...`.

Run: uv run --package nicegui-kit pytest nicegui-kit -q
"""

import asyncio
import sys
from uuid import uuid4

import pytest

from nicegui_kit import run_pool

SLEEP_LONG = [sys.executable, "-c", "import time; time.sleep(30)"]
SLEEP_SHORT = [sys.executable, "-c", "import time; time.sleep(0.3)"]
PRINT_OK = [sys.executable, "-c", "print('hello')"]
PRINT_LINES = [sys.executable, "-c", "print('one'); print('two')"]
EXIT_THREE = [sys.executable, "-c", "import sys; sys.exit(3)"]


@pytest.fixture(autouse=True)
def _pool():
    """Чистый пул на 2 слота для каждого теста."""
    run_pool.reset_pool_for_tests(max_parallel=2)
    yield
    run_pool.reset_pool_for_tests()


class _Spawner:
    """asyncio.create_task + запоминание таск, чтобы дождаться их до конца теста."""

    def __init__(self) -> None:
        self.tasks: list[asyncio.Task] = []

    def __call__(self, coro, name: str | None = None) -> asyncio.Task:
        task = asyncio.create_task(coro, name=name)
        self.tasks.append(task)
        return task

    async def drain(self, timeout: float = 10.0) -> None:
        if self.tasks:
            await asyncio.wait_for(
                asyncio.gather(*self.tasks, return_exceptions=True), timeout,
            )


def _no_spawn(coro, name: str | None = None) -> None:
    """Для синхронных тестов: жизненный цикл не нужен, корутину закрываем."""
    coro.close()


def _fabricate(status: str):
    """Готовый RunState прямо в RUNS — для тестов истории/лимитов без подпроцессов."""
    state = run_pool.RunState(run_id=uuid4().hex[:8], argv=[], status=status)
    run_pool.RUNS[state.run_id] = state
    return state


async def _wait_until(predicate, timeout: float = 5.0) -> bool:
    loop = asyncio.get_running_loop()
    deadline = loop.time() + timeout
    while loop.time() < deadline:
        if predicate():
            return True
        await asyncio.sleep(0.01)
    return predicate()


# --- 1-2: слоты и очередь ---------------------------------------------------


def test_third_run_waits_in_queue_when_both_slots_are_busy() -> None:
    async def scenario() -> None:
        spawner = _Spawner()
        for _ in range(2):
            run_pool.submit(SLEEP_LONG, spawn=spawner)
        third = run_pool.submit(SLEEP_LONG, spawn=spawner)
        assert await _wait_until(lambda: len(run_pool.active_runs()) == 2)
        assert third is not None
        assert third.status == "queued"
        assert third.process is None
        assert run_pool.queued_position(third) == 1
        for state in list(run_pool.RUNS.values()):
            run_pool.request_cancel(state.run_id)
        await spawner.drain()

    asyncio.run(scenario())


def test_freed_slot_starts_the_next_queued_run_in_fifo_order() -> None:
    async def scenario() -> None:
        spawner = _Spawner()
        blockers = [run_pool.submit(SLEEP_SHORT, spawn=spawner) for _ in range(2)]
        third = run_pool.submit(PRINT_OK, spawn=spawner)
        fourth = run_pool.submit(PRINT_OK, spawn=spawner)
        assert third is not None and fourth is not None
        assert await _wait_until(lambda: len(run_pool.active_runs()) == 2)
        assert third.status == "queued" and fourth.status == "queued"
        assert run_pool.queued_position(fourth) == 2
        await spawner.drain()
        assert [state.status for state in run_pool.RUNS.values()] == ["done"] * 4
        assert third.started_at is not None and fourth.started_at is not None
        assert third.started_at <= fourth.started_at
        for blocker in blockers:
            assert blocker is not None and blocker.started_at is not None
            assert blocker.started_at <= third.started_at

    asyncio.run(scenario())


# --- 3-4: отмена ------------------------------------------------------------


def test_cancelling_a_queued_run_never_spawns_a_subprocess() -> None:
    async def scenario() -> None:
        spawner = _Spawner()
        for _ in range(2):
            run_pool.submit(SLEEP_LONG, spawn=spawner)
        queued = run_pool.submit(SLEEP_LONG, spawn=spawner)
        assert queued is not None
        assert await _wait_until(lambda: len(run_pool.active_runs()) == 2)
        assert run_pool.request_cancel(queued.run_id) is True
        assert queued.status == "cancelled"
        for state in run_pool.active_runs():
            run_pool.request_cancel(state.run_id)
        await spawner.drain()
        assert queued.process is None
        assert queued.started_at is None
        assert queued.status == "cancelled"

    asyncio.run(scenario())


def test_cancelling_a_running_run_kills_the_process() -> None:
    async def scenario() -> None:
        spawner = _Spawner()
        state = run_pool.submit(SLEEP_LONG, spawn=spawner)
        assert state is not None
        assert await _wait_until(lambda: state.status == "running")
        assert run_pool.request_cancel(state.run_id) is True
        await spawner.drain()
        assert state.status == "cancelled"
        assert state.process is not None and state.process.returncode is not None
        assert state.finished_at is not None

    asyncio.run(scenario())


def test_cancel_while_the_process_is_still_spawning_is_not_lost(monkeypatch) -> None:
    real_exec = asyncio.create_subprocess_exec
    accepted: list[bool] = []

    async def exec_with_cancel_mid_spawn(*args, **kwargs):
        # окно между status=RUNNING и присваиванием state.process
        accepted.extend(run_pool.request_cancel(rid) for rid in list(run_pool.RUNS))
        return await real_exec(*args, **kwargs)

    monkeypatch.setattr(run_pool.asyncio, "create_subprocess_exec", exec_with_cancel_mid_spawn)

    async def scenario() -> None:
        spawner = _Spawner()
        state = run_pool.submit(SLEEP_LONG, spawn=spawner)
        assert state is not None
        await spawner.drain()
        assert accepted == [True]
        assert state.status == "cancelled"
        assert state.process is not None and state.process.returncode is not None

    asyncio.run(scenario())


# --- 5-6: финальные статусы и лог -------------------------------------------


def test_successful_run_collects_the_log_and_calls_on_line() -> None:
    async def scenario() -> None:
        spawner = _Spawner()
        seen: list[str] = []
        state = run_pool.submit(PRINT_LINES, spawn=spawner, on_line=seen.append)
        assert state is not None
        await spawner.drain()
        assert state.status == "done"
        assert state.return_code == 0
        assert state.lines == ["one", "two"]
        assert seen == ["one", "two"]

    asyncio.run(scenario())


def test_crlf_line_endings_are_stripped() -> None:
    async def scenario() -> None:
        spawner = _Spawner()
        crlf = [sys.executable, "-c", "import sys; sys.stdout.buffer.write(b'one\\r\\ntwo\\r\\n')"]
        state = run_pool.submit(crlf, spawn=spawner)
        assert state is not None
        await spawner.drain()
        assert state.lines == ["one", "two"]

    asyncio.run(scenario())


def test_raising_on_line_callback_does_not_kill_the_run() -> None:
    def boom(line: str) -> None:
        raise RuntimeError("ui.* from background task")

    async def scenario() -> None:
        spawner = _Spawner()
        state = run_pool.submit(PRINT_LINES, spawn=spawner, on_line=boom)
        assert state is not None
        await spawner.drain()
        assert state.status == "done"
        assert state.lines == ["one", "two"]

    asyncio.run(scenario())


def test_nonzero_exit_code_marks_the_run_failed() -> None:
    async def scenario() -> None:
        spawner = _Spawner()
        state = run_pool.submit(EXIT_THREE, spawn=spawner)
        assert state is not None
        await spawner.drain()
        assert state.status == "failed"
        assert state.return_code == 3

    asyncio.run(scenario())


def test_missing_executable_marks_the_run_failed_not_cancelled() -> None:
    async def scenario() -> None:
        spawner = _Spawner()
        state = run_pool.submit(["/nonexistent/definitely-not-a-binary"], spawn=spawner)
        assert state is not None
        await spawner.drain()
        assert state.status == "failed"
        assert state.lines and "definitely-not-a-binary" in state.lines[-1]

    asyncio.run(scenario())


def test_output_line_longer_than_stream_limit_does_not_kill_the_run() -> None:
    long_line = [sys.executable, "-c", "print('x' * 200_000); print('tail')"]

    async def scenario() -> None:
        spawner = _Spawner()
        state = run_pool.submit(long_line, spawn=spawner)
        assert state is not None
        await spawner.drain()
        assert state.status == "done"
        assert state.lines[-1] == "tail"

    asyncio.run(scenario())


# --- 7-8: история и предохранитель очереди ----------------------------------


def test_finished_history_is_capped_and_active_runs_are_never_evicted() -> None:
    running = _fabricate("running")
    queued = _fabricate("queued")
    finished = [_fabricate("done") for _ in range(run_pool.FINISHED_HISTORY_LIMIT + 1)]
    fresh = run_pool.submit(PRINT_OK, spawn=_no_spawn)
    assert fresh is not None
    assert finished[0].run_id not in run_pool.RUNS  # старейший завершённый вытеснен
    assert finished[1].run_id in run_pool.RUNS
    assert running.run_id in run_pool.RUNS
    assert queued.run_id in run_pool.RUNS
    assert fresh.run_id in run_pool.RUNS


def test_submit_rejects_when_total_pending_limit_is_reached() -> None:
    for _ in range(run_pool.MAX_TOTAL_PENDING - 1):
        _fabricate("queued")
    _fabricate("running")
    assert run_pool.submit(PRINT_OK, spawn=_no_spawn) is None
    assert len(run_pool.RUNS) == run_pool.MAX_TOTAL_PENDING


# --- 9: cancel-safety (teardown NiceGUI) ------------------------------------


def test_cancelling_the_lifecycle_task_terminates_the_subprocess() -> None:
    async def scenario() -> None:
        tasks: list[asyncio.Task] = []
        state = run_pool.submit(
            SLEEP_LONG,
            spawn=lambda coro, name=None: tasks.append(asyncio.create_task(coro, name=name)),
        )
        assert state is not None
        assert await _wait_until(lambda: state.process is not None)  # RUNNING ставится до спавна
        tasks[0].cancel()
        with pytest.raises(asyncio.CancelledError):
            await tasks[0]
        assert state.process is not None
        assert await asyncio.wait_for(state.process.wait(), 5) != 0
        assert state.status == "cancelled"

    asyncio.run(scenario())


# --- 10: env/label snapshot at enqueue time ---------------------------------


def test_env_and_meta_are_snapshotted_at_submit_time() -> None:
    async def scenario() -> None:
        env = {"KEY": "first"}
        state = run_pool.submit(
            PRINT_OK, spawn=_no_spawn, label="collect prod-kz", env=env, meta={"env_name": "prod-kz"},
        )
        assert state is not None
        env["KEY"] = "second"  # caller mutates its own dict afterwards
        assert state.env["KEY"] == "first"
        assert state.label == "collect prod-kz"
        assert state.meta == {"env_name": "prod-kz"}

    asyncio.run(scenario())


def test_live_runs_and_all_runs_helpers() -> None:
    queued = _fabricate("queued")
    running = _fabricate("running")
    done = _fabricate("done")
    assert set(state.run_id for state in run_pool.live_runs()) == {queued.run_id, running.run_id}
    assert set(state.run_id for state in run_pool.all_runs()) == {
        queued.run_id, running.run_id, done.run_id,
    }


# --- 11: grace-период на выключении сервера ---------------------------------

# Печатает `ready` уже после установки обработчика: без этой синхронизации SIGTERM
# успевает прийти до неё и убивает процесс, который тест считает непослушным.
SLEEP_STUBBORN = [
    sys.executable, "-c",
    "import signal, time; signal.signal(signal.SIGTERM, lambda *a: None); "
    "print('ready', flush=True); time.sleep(30)",
]


def test_grace_period_waits_for_the_child_to_exit_on_its_own() -> None:
    async def scenario() -> None:
        spawner = _Spawner()
        state = run_pool.submit(SLEEP_LONG, spawn=spawner)
        assert state is not None
        assert await _wait_until(lambda: state.process is not None)

        await run_pool.terminate_all_live_processes(grace_seconds=5)

        # без ожидания returncode здесь ещё None — в этом весь смысл параметра
        assert state.process is not None and state.process.returncode is not None
        await spawner.drain()

    asyncio.run(scenario())


@pytest.mark.skipif(sys.platform == "win32", reason="terminate() is TerminateProcess on Windows: SIGTERM can't be caught")
def test_grace_period_returns_when_the_budget_runs_out_and_leaves_the_child_alive() -> None:
    async def scenario() -> None:
        spawner = _Spawner()
        seen: list[str] = []
        state = run_pool.submit(SLEEP_STUBBORN, spawn=spawner, on_line=seen.append)
        assert state is not None
        assert await _wait_until(lambda: "ready" in seen)

        await asyncio.wait_for(run_pool.terminate_all_live_processes(grace_seconds=0.3), 5)

        assert state.process is not None and state.process.returncode is None
        state.process.kill()  # тест не оставляет за собой живых процессов
        await spawner.drain()

    asyncio.run(scenario())
