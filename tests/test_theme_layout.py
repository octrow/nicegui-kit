"""theme.py / layout.py: pure checks + one page rendered through nicegui.testing.User.

`apply_theme()` and the layout helpers need a running page (they call `ui.*`
inside a client slot-stack), so the one integration test below uses NiceGUI's
own `user` pytest fixture (nicegui.testing) instead of mocking the UI away.
"""

from pathlib import Path

import pytest
from nicegui import ui
from nicegui.testing import User

from nicegui_kit import layout, theme


def test_font_dir_resolves_under_the_installed_package() -> None:
    assert theme.FONT_DIR == Path(theme.__file__).parent / "assets" / "fonts"
    assert theme.FONT_FILE.name == "InterVariable.woff2"


def test_font_file_ships_with_the_package() -> None:
    assert theme.FONT_FILE.is_file()


def test_theme_css_defines_the_ic_status_classes() -> None:
    assert ".ic-status--running" in theme._THEME_CSS
    assert ".ic-status--error" in theme._THEME_CSS


def test_contrast_formula_matches_wcag_extremes() -> None:
    assert theme.contrast("#000000", "#FFFFFF") > 20.9
    assert theme.contrast("#777777", "#777777") == 1


def test_both_themes_define_the_same_tokens() -> None:
    assert theme.TOKENS["dark"].keys() == theme.TOKENS["light"].keys()


@pytest.mark.parametrize("mode", ["light", "dark"])
def test_every_text_pair_reads_at_aa_in_both_themes(mode: str) -> None:
    tokens = theme.TOKENS[mode]
    weak = [(fg, bg, round(theme.contrast(tokens[fg], tokens[bg]), 2))
            for fg, bg in theme.TEXT_PAIRS if theme.contrast(tokens[fg], tokens[bg]) < 4.5]
    assert not weak


def _blend(fg: str, bg: str, alpha: float) -> str:
    mix = (round(int(fg[i:i + 2], 16) * alpha + int(bg[i:i + 2], 16) * (1 - alpha)) for i in (1, 3, 5))
    return "#" + "".join(f"{c:02X}" for c in mix)


@pytest.mark.parametrize("mode", ["light", "dark"])
def test_status_badges_read_at_aa_on_their_own_tint(mode: str) -> None:
    tokens = theme.TOKENS[mode]
    for status in ("run", "ok", "err", "idle"):
        for page in ("surface", "canvas", "surface-sunken"):
            tint = _blend(tokens[status], tokens[page], 0.10)  # .ic-badge: 10% currentColor
            assert theme.contrast(tokens[status], tint) >= 4.5, (mode, status, page)


def test_css_carries_dark_tokens_and_no_tailwind_gaps_in_helpers() -> None:
    css = theme.css()
    assert "body.body--dark {" in css and "--ic-s4: 16px;" in css
    assert "prefers-reduced-motion" in css
    sources = (Path(layout.__file__).read_text() + Path(theme.__file__).parent.joinpath(
        "run_monitor.py").read_text())
    assert '"gap-' not in sources and " gap-" not in sources.replace("Tailwind gap-*", "")


def test_heading_uses_the_right_tag_and_class_for_each_level() -> None:
    assert layout.HEADING_CLASSES[1] == "t-title-page"
    assert layout.HEADING_CLASSES[2] == "t-title-section"


def test_css_carries_type_scale_motion_grid_and_touch_targets() -> None:
    css = theme.css()
    assert "--ic-fs-xl: 1.75rem;" in css and "--ic-ease-out:" in css
    assert ".ic-grid-12 > .ic-span-12 { grid-column: span 12; }" in css
    assert "@media (pointer: coarse)" in css and "--ic-h-ctl: 44px;" in css
    assert "font-size: 1.75rem" not in theme._THEME_CSS  # roles read the scale


def test_field_kinds_cover_keyboard_and_autofill() -> None:
    assert layout.FIELD_KINDS["email"]["inputmode"] == "email"
    assert layout.FIELD_KINDS["new-password"]["autocomplete"] == "new-password"
    assert layout.FIELD_KINDS["code"]["autocomplete"] == "one-time-code"


@ui.page("/form")
def _form_page() -> None:
    theme.apply_theme()
    with layout.grid():
        layout.field("Почта", kind="email", required=True, hint="Рабочая почта").classes("ic-span-6")
        layout.field("Город", suggestions=["Москва", "Минск"]).classes("ic-span-6")
    layout.search_field("Поиск по названию")
    ui.toggle(["день", "всё"], value="всё")


@pytest.mark.nicegui_main_file(__file__)
async def test_field_sets_native_attrs_and_validates_on_blur(user: User) -> None:
    await user.open("/form")
    inputs = [el for el in user.current_layout.descendants() if isinstance(el, ui.input)]
    email = next(i for i in inputs if i.props.get("label") == "Почта")
    assert email.props["inputmode"] == "email" and email.props["aria-required"] == "true"
    assert email.props["hint"] == "Рабочая почта" and "ic-required" in email.classes
    assert email.error is None  # nothing shown before the user leaves the field
    assert not email.validate()
    assert email.error == "Заполните поле «Почта»"
    email.value = "a@b.c"  # a fix clears the error at once, no blur needed
    assert email.error is None
    grids = [el for el in user.current_layout.descendants() if "ic-grid-12" in el.classes]
    assert grids
    city = next(i for i in inputs if i.props.get("label") == "Город")
    assert "bottom-slots" in city.props  # same space under every field: an even rhythm, hint or not
    assert "stack-label" in email.props  # the label sits on top even when empty: never mistaken for a placeholder


@pytest.mark.nicegui_main_file(__file__)
async def test_search_field_is_self_describing_and_toggle_selection_is_tonal(user: User) -> None:
    await user.open("/form")
    inputs = [el for el in user.current_layout.descendants() if isinstance(el, ui.input)]
    search = next(i for i in inputs if i.props.get("placeholder") == "Поиск по названию")
    assert search.props["aria-label"] == "Поиск по названию" and not search.props.get("label")
    assert search.props["inputmode"] == "search"
    toggle = next(el for el in user.current_layout.descendants() if isinstance(el, ui.toggle))
    assert toggle.props["toggle-color"] == "ic-sel"  # a soft fill, not a second primary button
    assert ".bg-ic-sel" in theme.css() and ("accent-800", "accent-100") in theme.TEXT_PAIRS


@ui.page("/")
def _demo_page() -> None:
    theme.apply_theme()
    with ui.header():
        theme.theme_toggle()
    with layout.page_container(max_width=layout.PAGE_MAX_WIDTH_WIDE):
        layout.heading("Demo", level=1)
        with layout.section_card():
            ui.label("hello")
            with layout.actions_row():
                layout.button("Go", kind="primary")
        layout.empty("nothing yet")
        layout.waiting()
        layout.failed("it broke", retry=lambda: None)
        with layout.filter_bar():
            ui.label("filter placeholder")
        layout.markdown_reader("**bold** text", max_height="60vh")


@pytest.mark.nicegui_main_file(__file__)
async def test_apply_theme_and_layout_helpers_render_without_error(user: User) -> None:
    await user.open("/")
    await user.should_see("Demo")
    await user.should_see("hello")
    await user.should_see("filter placeholder")
    await user.should_see("bold")
    await user.should_see("nothing yet")
    await user.should_see("Повторить")
    user.find("Go").click()

    buttons = [el for el in user.current_layout.descendants() if isinstance(el, ui.button)]
    assert any("ic-btn-ctl" in b.classes and "unelevated" in b.props for b in buttons)
    toggle = next(b for b in buttons if b.props.get("icon") == theme.THEME_MODES["system"][0])
    assert "color" not in toggle.props  # header ink, not the accent: it is not the page's main action

    rows = [el for el in user.current_layout.descendants() if isinstance(el, ui.row)]
    assert any("ic-filters" in row.classes for row in rows)

    columns = [el for el in user.current_layout.descendants() if isinstance(el, ui.column)]
    md_columns = [c for c in columns if "md-body" in c.classes]
    assert md_columns
    assert any(c.style.get("max-height") == "60vh" for c in md_columns)


if __name__ in {"__main__", "__mp_main__"}:
    # nicegui's `user` fixture runs this file with runpy (run_name="__main__") to
    # build its simulated app - it needs an actual ui.run() call to do that.
    ui.run(storage_secret="test")


def test_kit_css_uses_only_tokens() -> None:
    assert theme.raw_values(theme._THEME_CSS) == []


def test_raw_values_catches_off_system_css() -> None:
    bad = (".a { font-weight: 600; line-height: 1.4; border-radius: 6px; font-size: 13px;"
           " padding: 0.5rem; gap: 12px; color: #fff; box-shadow: 0 1px 2px rgb(0 0 0 / .1); }")
    assert len(theme.raw_values(bad)) == 8
    ok = (".a { font-weight: var(--ic-fw-bold); padding: 1px var(--ic-s2); border-radius: 0;"
          " margin: 0; font-size: 0.875em; border: 1px solid var(--ic-border); }")
    assert theme.raw_values(ok) == []
