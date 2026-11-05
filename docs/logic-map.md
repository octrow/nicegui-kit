# Logic map

How one command line becomes a finished run that a NiceGUI page lists, streams and can stop.
The map describes the code as it is today, step by step.
Each step says what it decides, where the flow branches, and which module does it.

The kit has one stateful flow (the run pool and its monitor, steps 1-9) and four stateless helper groups (side flows).
Terms: a run is one `RunState`; a slot is one of `MAX_PARALLEL_RUNS` semaphore permits; the pool is the process-global `RUNS` dict.
Known gaps and fixes in progress are in `docs/plans/2026-11-05-logic-map-fixes.md`.

Rule: if you change a step or a branch, update this file in the same commit.
`tests/test_logic_map.py` checks that every `Module:` line points to a real module.

## The flow at a glance

```
argv + options
  │
  ├─ 1  submit ............... is there room (queued+running < 20)? make RunState
  ├─ 2  wait for a slot ...... skip if cancelled while queued
  ├─ 3  spawn ................ did the process start? else FAILED
  ├─ 4  pump output .......... merged stdout+stderr -> lines, on_line
  ├─ 5  final status ......... DONE / FAILED / CANCELLED from exit code + cancel flag
  ├─ 6  finalize ............. terminate leftovers, stamp finished_at (always runs)
  ├─ 7  cancel ............... queued: at once; running: SIGTERM; spawning: flag
  ├─ 8  monitor tick ......... 1 Hz: create / mutate / delete widgets per run
  └─ 9  shutdown ............. SIGTERM all live children, optional grace wait
  │
RunState in RUNS, shown as expansion rows with a live log
```

Nothing in steps 1-7 touches `ui.*`: background tasks have no slot stack.
Only step 8 builds widgets.

## Where the flow splits by language and status

Status decides labels and CSS in one place (`run_status_text`); language is one global dict.

| Variant | Switched on by | Steps it changes | What changes |
|---|---|---|---|
| status `queued/running/done/cancelled` | `RunState.status` | 8 | label text, badge class, cancel button visible, button text "Remove from queue" vs "Stop" |
| status `failed` with `return_code` | status + code | 8 | `error · code N`; no code (spawn failed) -> plain `error`; css class is the fallback `ic-status--error` |
| language | `texts.TEXTS` (RU default, `texts.EN` via `update`) | 3, 4, 8, side flows | every user string; `lines` plural function |
| theme mode | browser localStorage key `nicegui-kit-theme` | Theme flow | `ui.dark_mode` value |

Examples:
- `submit(["nope"])` -> step 3 fails, log line `failed to start: ...`, status `failed`, no return code, badge `error`.
- Stop pressed on a queued run -> step 7 queued branch, status `cancelled`, the run never spawns.

Module: `texts`, `run_monitor`

## Entry points

All public functions are called from the app's own page or startup code. There is no CLI.

| Entry | Defaults | Notes |
|---|---|---|
| `run_pool.submit(argv, ...)` | `label=""`, `cwd=None`, `env=None` -> `{}` -> child inherits the parent env, `meta=None` -> `{}`, `on_line=None`, `spawn=background_tasks.create` | side effect: stores the run in the global `RUNS` and may drop old finished runs; returns `None` when 20 runs are queued or running; call it where an event loop is running |
| `run_pool.request_cancel(run_id)` | none | `False` when the run is unknown or already finished |
| `run_pool.terminate_all_live_processes(grace_seconds=0.0)` | no wait | for `app.on_shutdown`; SIGTERM to direct children only; skips runs still spawning (`process` is `None`); does not change any `RunState.status` |
| `run_monitor.attach_run_monitor(...)` | poll 1.0 s, log DOM cap 2000 lines, copy tail 15 lines, no filter | call inside a page; one timer per page client |
| `theme.apply_theme()` | none | once before `ui.run()`; sets Quasar colors, injects CSS in `<head>` |
| `theme.theme_toggle()` | mode `system` | once per page, inside the header |
| `layout.*`, `table.empty_aware_table`, `hotkeys.on_keydown` | see side flows | pure widget builders |
| `run_pool.reset_pool_for_tests(max_parallel=None)` | 3 slots | side effect: clears `RUNS` and drops the semaphore; the only way to change the slot count (`MAX_PARALLEL_RUNS` is copied at import) |

Module: `run_pool`, `run_monitor`, `theme`, `layout`, `table`, `hotkeys`

## Steps

### 1. Submit

Decides: whether the run is accepted.
In: `argv`, options. Out: `RunState` (status `queued`) or `None`.
Branches:
- queued + running >= `MAX_TOTAL_PENDING` (20) -> return `None`, nothing stored;
- otherwise -> `RunState` with a copy of `argv`, `meta`, `env`, stored in `RUNS` under an 8-hex id.
After storing, the pool drops the oldest finished runs beyond `FINISHED_HISTORY_LIMIT` (20); queued and running runs are never dropped.
Then the lifecycle coroutine is handed to `spawn`.
Fails: if `spawn` raises (for example no event loop: `background_tasks.create` asserts `core.loop`), the exception reaches the caller but the run stays `queued` in `RUNS` and counts toward the 20 until someone cancels it (#1).
Module: `run_pool`

### 2. Wait for a slot

Decides: when the run may start, and whether it starts at all.
In: `RunState`. Out: the slot is held, or the run ends.
Branches:
- slot free -> continue;
- all slots busy -> wait in the semaphore, FIFO;
- on getting the slot, status is `cancelled` or the cancel flag is set -> return without starting.
A run cancelled while queued keeps its task waiting in the semaphore; it takes the slot for a moment and releases it.
The semaphore is created on first use inside the running loop, with `_MAX_PARALLEL` permits (3).
Module: `run_pool`

### 3. Spawn

Decides: whether the process started.
In: `argv`, `cwd`, `env`. Out: `state.process`, status `running`, `started_at`.
Branches:
- `OSError`, `ValueError`, `TypeError` from `create_subprocess_exec` -> log line `failed to start: ...`, status `failed`, no return code; an empty `argv` raises `IndexError` inside this handler and ends `cancelled` with no log line (#8);
- status is set to `running` before the spawn starts; cancel flag set while spawning -> `terminate()` right after the process exists;
- `env` empty or `None` -> child inherits the parent env; non-empty `env` replaces it entirely, no merge (#2).
stderr is merged into stdout; the stream limit is 1 MiB per line.
Fails: any other exception skips to step 6, which marks the run `cancelled` (not `failed`), and propagates to the background task (#8).
Module: `run_pool`

### 4. Pump output

Decides: nothing; copies the output.
In: the process pipe. Out: `state.lines`, one `on_line(line)` call per line.
Branches:
- line longer than the limit -> the log gets `overlong_line` text, reading continues; if the line arrives in one piece it is dropped, if it streams in chunks the log gets one marker per overflowing chunk plus the line's last fragment;
- `on_line` raises -> logged with `logger.exception`, reading continues;
- EOF -> stop. EOF comes when every holder of the pipe closes it, so a grandchild that inherited stdout keeps the run here after the child exits (#9).
Lines are decoded with `errors="replace"`, trailing `\r\n` stripped. `lines` is never capped here. The `overlong_line` marker is not passed to `on_line`.
Module: `run_pool`, `texts`

### 5. Final status

Decides: the end status.
In: exit code, cancel flag. Out: `return_code`, `status`.
Branches:
- cancel flag set -> `cancelled`, whatever the exit code;
- exit code 0 -> `done`;
- any other code (including a negative signal code) -> `failed`.
Module: `run_pool`

### 6. Finalize

Decides: cleanup on every exit path, including task cancellation at NiceGUI shutdown.
Branches:
- process still running (task cancelled) -> `terminate()` once to the direct child; no `kill` follows (#3, #9);
- status still `queued` or `running` -> `cancelled`;
- `finished_at` unset -> now (UTC).
Module: `run_pool`

### 7. Cancel

Decides: how a stop request acts.
In: `run_id`. Out: `True` if something was stopped.
Branches:
- unknown or finished run -> `False`;
- `queued` -> flag, status `cancelled`, `finished_at` now, immediately;
- `running`, process not yet created -> flag only; step 3 terminates it;
- `running`, process alive -> flag, `terminate()` (SIGTERM); status arrives from step 5;
- `running`, process already exited -> `False`; this lasts as long as a grandchild holds the pipe, so Stop does nothing then (#9).
SIGTERM goes to the direct child only, not its process group: a grandchild survives and keeps the run `running` until it exits (#9).
A process that ignores SIGTERM keeps its slot (#3).
Module: `run_pool`

### 8. Monitor tick

Decides: which widgets exist and what they show.
In: `RUNS`. Out: one expansion row per run, in pool order.
Every `poll_interval_seconds` the tick:
- creates a row for each run without one; a row created in this tick is opened only when its run is the last in the pool (first page load: only the newest);
- sets the row visible by `run_filter` (default: all); filtered rows are kept, never deleted;
- updates status text and badge class, duration (`M:SS`), cancel button (visible while queued/running), copy button (visible when there are lines);
- pushes only new lines into `ui.log`, one at a time: a fresh row gets the whole `lines` list at once (#10); `ui.log.push` splits on `splitlines()`, so a blank line adds nothing and a line with `\r` adds several (#11);
- sets the caption and the log height (1 to 14) from `len(state.lines)`, not from the DOM;
- deletes rows whose run left the pool;
- shows the idle label when no row is visible.
The cancel button opens a confirm dialog (a new `ui.dialog` per click, never deleted, #13); Confirm calls step 7.
The copy button writes `label: status` plus the last `error_tail_lines` lines to the clipboard; the log is not parsed.
Fails: a raising `run_filter` aborts the tick at that run: later rows, the idle label and row deletion are skipped; `ui.timer` logs it via `app.handle_exception` and retries next tick (#5).
Module: `run_monitor`, `layout`, `texts`

### 9. Shutdown

Decides: which children get SIGTERM at app stop.
Branches:
- every run whose process has no return code -> `terminate()` (direct child only, #9);
- `grace_seconds > 0` -> wait for all of them together up to that budget; survivors are left alive;
- queued runs are not touched here; statuses are not changed (step 6 does that when the tasks are cancelled).
Module: `run_pool`

### Output

`RunState`: `run_id, argv, label, meta, status, env, lines, process, return_code, created_at, started_at, finished_at, cancelled`.
Status constants: `queued, running, done, failed, cancelled`.
Helpers the page reads: `active_runs, queued_runs, live_runs, all_runs, queued_position, run_duration`.
Module: `run_pool`

## Side flows

### Theme

`apply_theme()` sets Quasar brand colors, default toggle props, and injects the token CSS (plus the `@font-face` when the Inter file exists, served at `/fonts`) into `<head>` for every page.
`theme_toggle()` cycles system -> light -> dark -> system, stores the choice in localStorage, and restores it after the client connects (once per page; a non-system choice flashes the system theme first; a toggle built after the handshake restores only on a reconnect, #6).
A client that does not answer the localStorage read in time keeps the system theme.
`raw_values(css)` lists declarations that bypass tokens; `luminance`/`contrast` back the contrast tests.
Feeds: step 8 (CSS classes `ic-*`, `t-*`).
Module: `theme`, `texts`

### Layout helpers

Widget builders with the kit spacing: `page_container, heading, section_card, filter_bar, actions_row, button, grid, field, search_field, empty, waiting, failed, markdown_reader, copy_for_chat_button`.
`field` validates on blur, then on every change while an error shows (only when it has rules: `required` or `validation`); `kind` picks keyboard and autofill attributes. Unknown `kind` or `button` kind raises `KeyError` after the widget is already built.
Feeds: step 8 (buttons, rows).
Module: `layout`, `texts`

### Table

`empty_aware_table` builds `ui.table` plus an empty label; `set_rows` swaps them by whether rows exist.
Columns carry `priority` (2 or 3 hide under a container width), `sub` (second line). The first column is `required` for Quasar, but a `priority` on it still hides it by CSS (#12).
Before the first `set_rows`, the table shows and the empty label is hidden.
`column_picker(key)` stores hidden columns in localStorage and restores them on every connect (same handshake limit, #6); a manual choice turns width-based hiding off.
Module: `table`, `layout`, `texts`

### Hotkeys and texts

`hotkeys.on_keydown` wraps `ui.keyboard`: runs the handler only on keydown with no Ctrl/Alt/Meta; ignores focus in `input, select, textarea`.
`texts.tr(key, **fmt)` reads the global `TEXTS` at call time; one language per server process.
Module: `hotkeys`, `texts`

## Known gaps

- A `spawn` that raises leaves a permanent `queued` run that eats pool capacity (#1).
- No SIGKILL escalation: a child ignoring SIGTERM keeps its slot and outlives cancel and shutdown (#3).
- An empty `env` means "inherit", a non-empty `env` means "replace" (#2).
- Cancel and shutdown signal only the direct child: grandchildren survive, and one holding stdout keeps the run `running` and un-stoppable (#9).
