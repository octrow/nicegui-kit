# nicegui-kit

[![CI](https://github.com/octrow/nicegui-kit/actions/workflows/ci.yml/badge.svg)](https://github.com/octrow/nicegui-kit/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/nicegui-kit)](https://pypi.org/project/nicegui-kit/)
[![Python](https://img.shields.io/pypi/pyversions/nicegui-kit)](https://pypi.org/project/nicegui-kit/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

**English** | [Русский](README.ru.md)

A theme and a small toolkit for [NiceGUI](https://nicegui.io) apps that run jobs: internal tools,
scrapers, admin panels, review queues. One call gives you a light and dark theme that passes WCAG AA,
a self-hosted Inter font (works offline), layout helpers with one spacing rhythm, and a subprocess pool
with a live log monitor that survives page reloads and cancels cleanly.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/images/runs-dark.png">
  <img alt="Sample job runner screen built with nicegui-kit: search, status filter, period toggle, a finished run and a failed run with its log open" src="docs/images/runs-light.png">
</picture>

The screen above is `examples/showcase.py`, about 200 lines on top of the kit. Kit strings are Russian
by default; `texts.TEXTS.update(texts.EN)` switches them to English.

## What you get

- A theme: light and dark tokens in one dict, every text/background pair tested at WCAG AA (4.5:1) in
  both themes, a header button that cycles system → light → dark and remembers the choice.
- Layout helpers: `page_container`, `heading`, `section_card`, `grid`, `field`, `filter_bar`,
  `button`, and the three states every data view needs: `empty`, `waiting`, `failed`.
- A run pool: `run_pool.submit(argv)` runs a subprocess with a slot limit, a queue cap and cancel that
  kills the process. No UI code inside, so it is testable on its own.
- A run monitor: `run_monitor.attach_run_monitor()` shows live runs with status, log and a cancel button.
  The poll timer updates widgets in place instead of rebuilding them, so expanded panels, log scroll and
  focus stay put.
- An agent skill: `.claude/skills/nicegui-kit-gui` teaches Claude Code (or another coding agent) to
  build screens on the kit.

## Install

```bash
pip install nicegui-kit
# or
uv add nicegui-kit
```

Python ≥3.12, `nicegui>=3.15,<4`.

## Quick start

```python
from nicegui import ui
from nicegui_kit import layout, run_pool, run_monitor, theme

theme.apply_theme()  # once, before ui.run() — colors/CSS shared across pages


@ui.page("/")
def index() -> None:
    with layout.page_container(max_width=layout.PAGE_MAX_WIDTH_WIDE):
        layout.heading("My tool", level=1)
        theme.theme_toggle()  # usually inside ui.header()
        with layout.section_card():
            layout.button("Run it", kind="primary", on_click=lambda: run_pool.submit(
                ["python", "-c", "print('hi')"], label="demo run",
            ))
        run_monitor.attach_run_monitor()


ui.run(host="127.0.0.1")
```

Run the full demo from a clone:

```bash
git clone https://github.com/octrow/nicegui-kit && cd nicegui-kit
uv run python examples/showcase.py   # http://127.0.0.1:8787, ?dark=1 forces dark
```

`/` is a sample working screen (start a run, watch the list); `/kit` is the component gallery:

<img alt="Component gallery: data states, status chips and a warning banner, input fields with hints, a table and a markdown block" src="docs/images/gallery-light.png">

## Why not plain NiceGUI?

NiceGUI gives you Quasar components and Tailwind classes, which is enough for one page. Across several
tools the same things get written again: colors that fail contrast in dark mode, a different gap on every
card, a subprocess launched from a button that blocks the event loop or leaves a zombie when the tab
closes, a log view that jumps to the top on every refresh. The kit fixes those once and tests them.

You still write `ui.*` code; the kit sits on top of NiceGUI, and each part of it works on its own. If you are building a data app around dataframes and charts rather
than jobs and forms, Streamlit or Gradio may fit better.

| module | what it is |
|---|---|
| `nicegui_kit.theme` | `apply_theme()` — light + dark tokens, typography, self-hosted Inter Variable; `theme_toggle()` header button |
| `nicegui_kit.layout` | `page_container` / `heading` / `section_card` / `grid` / `field` / `search_field` / `filter_bar` / `actions_row` / `button` / `empty` / `waiting` / `failed` / `markdown_reader` / `copy_for_chat_button` |
| `nicegui_kit.hotkeys` | `on_keydown()` — `ui.keyboard` wrapper: keydown-only, no modifier held |
| `nicegui_kit.table` | `empty_aware_table()` — a `ui.table` + its "nothing found" label, kept in sync by one call |
| `nicegui_kit.texts` | `TEXTS` — every kit string in one dict (Russian by default), `EN` for English |
| `nicegui_kit.run_pool` | `submit()` — slots + queue + cancel-safe subprocess lifecycle, no `ui.*` |
| `nicegui_kit.run_monitor` | `attach_run_monitor()` — live list of runs: status, log, cancel button |

The design rules behind the theme (tokens, type scale, do's and don'ts) are in [DESIGN.md](DESIGN.md).

## API

### `theme`

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

### `layout`

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
"2026 baseline" table in DESIGN.md.

Gaps come from kit classes (`ic-page`, `ic-card`, `ic-stack`, `ic-actions`,
`ic-state`, `ic-split`), never from Tailwind `gap-*` (NiceGUI #2171).

### `hotkeys`

`on_keydown(handler, *, ignore=("input", "select", "textarea"))` — a
`ui.keyboard` that calls `handler(event)` only on a plain keydown (not keyup,
no Ctrl held): the two guards every page-level hotkey binding needs before its
own key dispatch runs. `passes(event) -> bool` is the underlying predicate,
exposed as a pure function for testing without a running page.

### `table`

`empty_aware_table(columns, *, row_key, pagination=None, empty_text=...) ->
EmptyAwareTable` — a `ui.table` plus the label that replaces it when nothing
matches. Call `.set_rows(rows)` from your filter's refresh function; it
pushes the new rows and toggles table/label visibility to match. Only fits a
table that's built once and mutated in place on each filter change — a table
rebuilt from scratch on every render (e.g. inside `@ui.refreshable`) doesn't
need this.

### `run_pool`

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

### `run_monitor`

`attach_run_monitor(*, run_filter=None, idle_text=..., poll_interval_seconds=1.0,
log_max_lines=2000, error_tail_lines=15)` — a live list of runs from the pool:
status line, live log (`ui.log`), a cancel button behind a confirmation
dialog, and on failed runs one "Скопировать для чата" button (summary + last
log lines). The status is said once, coloured, in the run's header — visible
even collapsed; the log is the only copy of the output. The
main invariant: the poll timer **never**
rebuilds an existing run's widgets, only mutates them (NiceGUI has no virtual
DOM — rebuilding kills expansion state, log scroll position and focus).

## Out of scope

Domain logic stays in your app. The kit gives you the pieces to build it:

- Duplicate-run detection and "you are number N in the queue" wording: use `RunState.meta` and
  `run_pool.live_runs()`.
- Parsing a run's output for known error patterns: the failure summary is a plain "exit code N" line;
  read the log in `on_line` if you need more.

## Agent skill

`.claude/skills/nicegui-kit-gui/SKILL.md` teaches a coding agent to build GUIs on this kit (what to
mirror, the non-obvious NiceGUI traps). Claude Code picks it up by itself in sessions inside this repo;
install it to use it in your own projects:

```bash
# via the skills CLI (https://github.com/vercel-labs/skills); copies the skill, works with several agents
npx skills add octrow/nicegui-kit --skill nicegui-kit-gui -g -a claude-code   # global
npx skills add octrow/nicegui-kit --skill nicegui-kit-gui -a claude-code      # into ./.claude/skills of the current project
```

Refresh with `npx skills update nicegui-kit-gui`, remove with `npx skills remove nicegui-kit-gui`.

## Development

```bash
uv sync --extra dev
uv run pytest -q
```

Contributions are welcome, see [CONTRIBUTING.md](CONTRIBUTING.md). Security issues: [SECURITY.md](SECURITY.md).

## License

MIT, see [LICENSE](LICENSE). The bundled Inter font is under the SIL Open Font License 1.1, see
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
