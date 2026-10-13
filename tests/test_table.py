"""nicegui_kit.table: table + empty-label pair, kept in sync by set_rows()."""

import pytest
from nicegui import ui
from nicegui.testing import User

from nicegui_kit import table, texts

_COLUMNS = [{"name": "n", "label": "N", "field": "n"}]


@ui.page("/")
def _demo_page() -> None:
    pair = table.empty_aware_table(_COLUMNS, row_key="n", empty_text="nothing here")
    pair.set_rows([])  # start empty, same as a page load before the first filter
    with ui.row():
        ui.button("fill", on_click=lambda: pair.set_rows([{"n": 1}]))
        ui.button("empty", on_click=lambda: pair.set_rows([]))


@pytest.mark.nicegui_main_file(__file__)
async def test_starts_with_empty_label_shown(user: User) -> None:
    await user.open("/")
    await user.should_see("nothing here")


@pytest.mark.nicegui_main_file(__file__)
async def test_set_rows_toggles_table_and_label(user: User) -> None:
    await user.open("/")
    user.find("fill").click()
    await user.should_not_see("nothing here")

    user.find("empty").click()
    await user.should_see("nothing here")


def test_default_empty_text() -> None:
    assert texts.TEXTS["empty"] == "ничего не найдено."


if __name__ in {"__main__", "__mp_main__"}:
    ui.run(storage_secret="test")


_WIDE = [{"name": "repo", "label": "Repo", "field": "repo", "sub": "desc"},
         {"name": "stars", "label": "Stars", "field": "stars", "priority": 2},
         {"name": "lang", "label": "Lang", "field": "lang", "priority": 3}]


def test_priority_becomes_a_class_and_the_first_column_is_pinned() -> None:
    cols = table._decorate(_WIDE)
    assert [c["classes"] for c in cols] == ["ic-p1", "ic-p2", "ic-p3"]
    assert cols[0]["required"] and "required" not in cols[1]
    assert _WIDE[0].get("classes") is None  # input left as is


@ui.page("/wide")
def _wide_page() -> None:
    pair = table.empty_aware_table(_WIDE, row_key="repo")
    pair.set_rows([{"repo": "a/b", "desc": "about it", "stars": 3, "lang": "Py"}])
    pair.column_picker("test-cols")


@pytest.mark.nicegui_main_file(__file__)
async def test_picker_hides_a_column_and_turns_fit_off(user: User) -> None:
    await user.open("/wide")
    pair_table = user.find(ui.table).elements.pop()
    assert "body-cell" in pair_table.slots
    assert pair_table.props["visible-columns"] == ["repo", "stars", "lang"]
    user.find(ui.checkbox).elements  # menu is built
    user.find("Stars").click()
    assert pair_table.props["visible-columns"] == ["repo", "lang"]
    assert "ic-table--picked" in pair_table.classes
    user.find("По ширине окна").click()
    assert pair_table.props["visible-columns"] == ["repo", "stars", "lang"]
    assert "ic-table--picked" not in pair_table.classes
