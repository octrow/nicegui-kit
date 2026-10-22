"""`ui.keyboard` wrapper for the "single key decides something" pattern.

Every consumer that binds page-level hotkeys needs the same two guards before
its own dispatch logic runs: ignore key-up events (`ui.keyboard` fires both),
and ignore the combo when a modifier is held (Ctrl+ArrowDown is a browser
shortcut, not a page action). Copied by hand into tlf's digest ↑/↓ nav and
jobs' 1/2/3/s/u/j/k/o queue-triage keys before this existed.
"""

from collections.abc import Callable

from nicegui import ui
from nicegui.events import KeyEventArguments

DEFAULT_IGNORE = ["input", "select", "textarea"]


def passes(event: KeyEventArguments) -> bool:
    """True for a plain keydown (not keyup, no Ctrl/Alt/Meta held; Shift is fine,
    "?" needs it) — the two guards every
    hotkey handler needs before its own key dispatch. A pure predicate (no
    `ui.*` call), so it is testable without a running page.
    """
    mods = event.modifiers
    return event.action.keydown and not (mods.ctrl or mods.alt or mods.meta)


def on_keydown(
    handler: Callable[[KeyEventArguments], None],
    *,
    ignore: list[str] | None = None,
) -> ui.keyboard:
    """`ui.keyboard` that calls `handler(event)` only when `passes(event)`.
    `ignore` is the list of focused-tag names that suppress the binding
    entirely (default: text-entry elements), forwarded to `ui.keyboard` as-is.
    """

    def _filtered(event: KeyEventArguments) -> None:
        if passes(event):
            handler(event)

    return ui.keyboard(on_key=_filtered, ignore=DEFAULT_IGNORE if ignore is None else ignore)
