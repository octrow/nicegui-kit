"""run_monitor: a filter hides runs in place, so clearing it brings them back in pool order."""

import asyncio

import pytest
from nicegui import ui
from nicegui.testing import User

from nicegui_kit import run_monitor, run_pool, theme

# nicegui_main_file runs this file as a second module, so a module-level set would not be shared
# with the page; a return code the filter treats as "hidden" travels through run_pool.RUNS instead.
HIDE = -99
TICK = 0.05


@ui.page("/")
def _page() -> None:
    theme.apply_theme()
    run_monitor.attach_run_monitor(run_filter=lambda s: s.return_code != HIDE, poll_interval_seconds=TICK)


def _shown_titles(user: User) -> list[str]:
    return [
        el.text for el in user.current_layout.descendants()
        if isinstance(el, ui.label) and "ic-run-title" in el.classes
        and all(a.visible for a in el.ancestors(include_self=True))
    ]


def _hide(*run_ids: str) -> None:
    for state in run_pool.RUNS.values():
        state.return_code = HIDE if state.run_id in run_ids else 0


async def _ticks(n: int = 4) -> None:
    await asyncio.sleep(TICK * n)


@pytest.mark.nicegui_main_file(__file__)
@pytest.mark.parametrize("hidden_at_load", [False, True])
async def test_clearing_the_filter_restores_pool_order(user: User, hidden_at_load: bool) -> None:
    run_pool.RUNS.clear()
    for rid in ("a", "b", "c"):
        run_pool.RUNS[rid] = run_pool.RunState(run_id=rid, argv=["x"], label=rid, status=run_pool.DONE)
    try:
        if hidden_at_load:
            _hide("a", "b")
        await user.open("/")
        await _ticks()
        _hide("a", "b")
        await _ticks()
        assert _shown_titles(user) == ["c"]
        _hide()
        await _ticks()
        assert _shown_titles(user) == ["a", "b", "c"]
    finally:
        run_pool.RUNS.clear()


if __name__ in {"__main__", "__mp_main__"}:
    ui.run(storage_secret="test")
