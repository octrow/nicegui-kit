"""run_monitor: a failed run says its status once (in the header, coloured) and
offers one copy button; there is no second copy of the log."""

import pytest
from nicegui import ui
from nicegui.testing import User

from nicegui_kit import run_monitor, run_pool, theme


@ui.page("/")
def _page() -> None:
    theme.apply_theme()
    run_monitor.attach_run_monitor(poll_interval_seconds=0.05)


@pytest.mark.nicegui_main_file(__file__)
async def test_failed_run_shows_status_once_and_one_copy_button(user: User) -> None:
    run_pool.RUNS.clear()
    run_pool.RUNS["r1"] = run_pool.RunState(
        run_id="r1", argv=["x"], label="демо", status=run_pool.FAILED,
        return_code=3, lines=["start", "boom"],
    )
    try:
        await user.open("/")
        await user.should_see("ошибка · код 3")
        labels = [el for el in user.current_layout.descendants() if isinstance(el, ui.label)]
        assert sum("код 3" in (lbl.text or "") for lbl in labels) == 1
        assert any(lbl.text == "Вывод: 2 строки" for lbl in labels)
        assert sum("boom" in (lbl.text or "") for lbl in labels) == 1  # the log is the only copy
        buttons = [el for el in user.current_layout.descendants() if isinstance(el, ui.button)]
        copy = next(b for b in buttons if b.props.get("icon") == "content_copy")
        assert copy.text == "" and copy.props["aria-label"] == "Скопировать для чата"
        cancel = next(b for b in buttons if b.text == "Остановить")
        assert copy.visible and not cancel.visible
    finally:
        run_pool.RUNS.clear()


if __name__ in {"__main__", "__mp_main__"}:
    ui.run(storage_secret="test")
