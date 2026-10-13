"""nicegui_kit.hotkeys: keydown-only, no-modifier dispatch.

`passes()` is a pure predicate (no `ui.*` call) so it is tested directly with
hand-built `KeyEventArguments` — no page needed. `on_keydown()` wraps
`ui.keyboard`, which does need a client/page to construct, so that half is a
plain render-without-error smoke test via `nicegui.testing.User` (same pattern
as test_theme_layout.py's `test_apply_theme_and_layout_helpers_render_without_error`).
"""

import pytest
from nicegui import ui
from nicegui.events import KeyboardAction, KeyboardKey, KeyboardModifiers, KeyEventArguments
from nicegui.testing import User

from nicegui_kit import hotkeys


def _event(*, keydown: bool = True, ctrl: bool = False, key: str = "a") -> KeyEventArguments:
    return KeyEventArguments(
        sender=None,
        client=None,
        action=KeyboardAction(keydown=keydown, keyup=not keydown, repeat=False),
        modifiers=KeyboardModifiers(alt=False, ctrl=ctrl, meta=False, shift=False),
        key=KeyboardKey(name=key, code=key, location=0),
    )


def test_default_ignore_covers_text_entry_elements() -> None:
    assert hotkeys.DEFAULT_IGNORE == ["input", "select", "textarea"]


def test_passes_is_true_for_a_plain_keydown() -> None:
    assert hotkeys.passes(_event(keydown=True, ctrl=False)) is True


def test_passes_is_false_for_keyup() -> None:
    assert hotkeys.passes(_event(keydown=False, ctrl=False)) is False


def test_passes_is_false_when_ctrl_is_held() -> None:
    assert hotkeys.passes(_event(keydown=True, ctrl=True)) is False


@ui.page("/")
def _demo_page() -> None:
    hotkeys.on_keydown(lambda _e: None)
    hotkeys.on_keydown(lambda _e: None, ignore=["input"])
    ui.label("hotkeys attached")


@pytest.mark.nicegui_main_file(__file__)
async def test_on_keydown_renders_without_error(user: User) -> None:
    await user.open("/")
    await user.should_see("hotkeys attached")


if __name__ in {"__main__", "__mp_main__"}:
    ui.run(storage_secret="test")
