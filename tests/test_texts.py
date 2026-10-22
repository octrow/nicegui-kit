"""nicegui_kit.texts: one dict of UI strings, RU default, EN swap at call time."""

from nicegui_kit import run_monitor, run_pool, texts


def test_en_has_every_ru_key() -> None:
    assert texts.EN.keys() == texts.RU.keys()


def test_switch_is_read_at_call_time() -> None:
    state = run_pool.RunState(run_id="x", argv=["true"], status=run_pool.DONE)
    try:
        assert run_monitor.run_status_text(state)[0] == "готово"
        texts.TEXTS.update(texts.EN)
        assert run_monitor.run_status_text(state)[0] == "done"
        assert texts.tr("output", n=2, lines=texts.lines_word(2)) == "Output: 2 lines"
    finally:
        texts.TEXTS.update(texts.RU)


def test_russian_plurals() -> None:
    assert [texts.lines_word(n) for n in (1, 2, 5, 11, 21, 22, 112)] == [
        "строка", "строки", "строк", "строк", "строка", "строки", "строк"]


def test_failed_run_without_exit_code_does_not_show_none() -> None:
    state = run_pool.RunState(run_id="x", argv=["nope"], status=run_pool.FAILED)
    assert run_monitor.run_status_text(state) == ("ошибка", "ic-status--error")
