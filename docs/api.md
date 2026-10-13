# API reference

**English** | [Русский](api.ru.md)

## `theme`

`apply_theme()` calls `app.colors(...)` and injects one `<style>` block into
`<head>` (via `ui.add_head_html(..., shared=True)`) — no flash of unstyled
content. Call it **once, explicitly**, before `ui.run()`; it does nothing at
import time, so a consumer that doesn't want the theme never pays for it.

Colors live in one dict per theme, `theme.TOKENS["light" | "dark"]`, emitted as
`--ic-<name>` variables (`body.body--dark` switches them); spacing and control
heights in `theme.SIZES` (`--ic-s1`…`--ic-s8`, `--ic-h-ctl`, `--ic-h-row`).
Quasar's brand colors point at the variables, so `color=primary` follows the
theme. Pages follow `ui.dark_mode` (system by default);
`theme_toggle()` in a header cycles system → light → dark and keeps the choice
in localStorage. `theme.TEXT_PAIRS` lists every text/background pair; the tests
hold each at WCAG AA in both themes, so a new token comes with its pair.

CSS classes carry an `ic-` prefix, kept from the GUI the kit was extracted
from; renaming them would only break existing apps. The class list
covers status colors (`ic-status--running/ok/cancel/error/idle`), type roles
(`t-title-page`, `t-title-section`, `t-status`, `t-meta`, `t-mono`, `t-log`),
banners/failure cards (`ic-banner`, `ic-failure*`), env chips
(`ic-chip`, `ic-chip--neutral` — unused unless your app renders one) and
a markdown reading surface (`.md-body`). The font ships in
`nicegui_kit/assets/fonts/InterVariable.woff2` (SIL OFL 1.1, `LICENSE.txt`
alongside it) and is served at `/fonts/InterVariable.woff2` when present;
degrades to a Cyrillic-safe system stack otherwise.

## `layout`

`page_container()` — the one column every page puts its content into
(`PAGE_MAX_WIDTH_FORM` / `PAGE_MAX_WIDTH_WIDE`). `heading(text, level=1|2|3)` —
a real `h1`/`h2`/`h3` tag (screen-reader navigable) with the matching type
role. `section_card(recessive=False)` — a card with the kit's spacing rhythm.
`filter_bar()` — one row for filter controls (topic/status/text/...), the
`ic-filters` CSS convention (one control height, full-width stacking under
700px). `search_field(placeholder, *, on_change=None)` — the filter-bar
search: magnifier + placeholder + aria-label, no floating label, so it matches
the select and toggle beside it. `ui.toggle` selection is a tonal fill
(`toggle-color=ic-sel`, set by `apply_theme()`), never a second primary button.
`markdown_reader(text, *, classes="", max_height=None)` — a `.md-body`
reading surface holding `ui.markdown(text)`; pass `max_height` (e.g. `"60vh"`)
to make it independently scrollable in a dialog or side pane.
`copy_for_chat_button(text)` — one button that copies `text` to the clipboard
with a confirmation toast.

`button(text, *, kind="normal"|"primary"|"quiet"|"danger", size="ctl"|"row")` —
the one way to make a button (one `primary` per screen; `danger` stands apart).
`actions_row()` — right-aligned buttons at the end of a card or dialog.
`empty(text, action=None)`, `waiting(text)`, `failed(text, retry=None)` — the
three states every data view needs, same look everywhere.

`grid(min_col=None)` — 12-column grid (children `.classes("ic-span-N")`,
one column under 700px) or, with `min_col="18rem"`, an auto-fill grid.
`field(label, *, kind="text", required=False, hint=None, validation=None,
suggestions=None, enter=None)` — the kit's text input: right mobile keyboard
and autofill per `kind` (`FIELD_KINDS`), validation on blur, error clears as
soon as the value is fixed.

Kit strings are Russian by default and live in one dict: `texts.TEXTS.update(texts.EN)` for English,
or override single keys. Weights, leading, tracking, radii, shadows and measures are tokens
(`theme.WEIGHTS`, `LEADING`, `TRACKING`, `RADII`, `SHADOWS`, `MEASURES`); `theme.raw_values(css)`
lists declarations that bypass them, for an app's own test.

Type scale, motion and touch sizes are tokens too: `theme.TYPE_SCALE`
(`--ic-fs-*`), `theme.MOTION` (`--ic-dur-*`, `--ic-ease-*`),
`theme.SIZES_COARSE` (bigger targets under `pointer: coarse`). See the
"2026 baseline" table in [DESIGN.md](../DESIGN.md).

Gaps come from kit classes (`ic-page`, `ic-card`, `ic-stack`, `ic-actions`,
`ic-state`, `ic-split`), never from Tailwind `gap-*` (NiceGUI #2171).

## `hotkeys`

`on_keydown(handler, *, ignore=("input", "select", "textarea"))` — a
`ui.keyboard` that calls `handler(event)` only on a plain keydown (not keyup,
no Ctrl held): the two guards every page-level hotkey binding needs before its
own key dispatch runs. `passes(event) -> bool` is the underlying predicate,
exposed as a pure function for testing without a running page.

## `table`

`empty_aware_table(columns, *, row_key, pagination=None, empty_text=...) ->
EmptyAwareTable` — a `ui.table` plus the label that replaces it when nothing
matches. Call `.set_rows(rows)` from your filter's refresh function; it
pushes the new rows and toggles table/label visibility to match. Only fits a
table that's built once and mutated in place on each filter change — a table
rebuilt from scratch on every render (e.g. inside `@ui.refreshable`) doesn't
need this.

## `run_pool`

Cancel-safe subprocess pool: `MAX_PARALLEL_RUNS` slots, `MAX_TOTAL_PENDING`
queue cap, `FINISHED_HISTORY_LIMIT` history. `submit(argv, *, label="",
cwd=None, env=None, meta=None, on_line=None, spawn=None) -> RunState | None`
(`None` means the queue is full). `argv` is the full command line (executable
+ args) — the caller decides what to run and where; `on_line` fires per merged
stdout+stderr line (not called from a NiceGUI slot-stack — see the module
docstring for why `ui.*` must never go there). `request_cancel(run_id)`,
`async terminate_all_live_processes(grace_seconds=0.0)` (register it
with `app.on_shutdown` through a zero-argument wrapper —
`async def _stop(): await run_pool.terminate_all_live_processes()` — because NiceGUI
passes the `App` into a one-parameter handler, where it would land in `grace_seconds`;
`grace_seconds` waits for children after SIGTERM), `live_runs()`
(queued + running), `all_runs()`.

Each `RunState` has a `label: str` (shown in the UI) and a `meta: dict`
(anything your app wants to stash and read back later, e.g. for its own
duplicate-run detection).

## `run_monitor`

`attach_run_monitor(*, run_filter=None, idle_text=..., poll_interval_seconds=1.0,
log_max_lines=2000, error_tail_lines=15)` — a live list of runs from the pool:
status line, live log (`ui.log`), a cancel button behind a confirmation
dialog, and on failed runs one "Скопировать для чата" button (summary + last
log lines). The status is said once, coloured, in the run's header — visible
even collapsed; the log is the only copy of the output. The
main invariant: the poll timer **never**
rebuilds an existing run's widgets, only mutates them (NiceGUI has no virtual
DOM — rebuilding kills expansion state, log scroll position and focus).
