# Plan: logic map findings

Findings from writing `docs/logic-map.md` on 2026-11-05, plus an independent review the same day (#8-#13, corrections to #1, #5, #6, #7).
The map describes the code as it is; this file says what is wrong with it and what we propose. New findings are appended.
A fixed finding gets ✅ and the map is updated in the same commit.

Severity: HIGH: wrong result for the user. MEDIUM: worse result than it could be. LOW: noise, debt, docs.
"Question": not sure if bug or intent; the owner decides. "Not confirmed": needs a live run.

## Findings

| # | Map step | What is wrong | We propose | Severity |
|---|---|---|---|---|
| 1 ✅ 2026-11-05 | 1 | `run_pool.py:135-138`: the `RunState` is stored in `RUNS` before `spawner(...)` runs; `background_tasks.create` asserts `core.loop is not None` (nicegui `background_tasks.py:48`) and raises without a loop, so the run stays `queued` until someone cancels it, counts toward `MAX_TOTAL_PENDING`, and the lifecycle coroutine is never awaited (RuntimeWarning). The caller does get the exception | on a `spawn` exception remove the run from `RUNS` (or mark it `failed`) and re-raise | MEDIUM |
| 2 | 3, Entry points | `run_pool.py:133,186`: `env=None` and `env={}` both become `{}`, then `state.env or None` makes the child inherit the parent env; a non-empty `env` replaces it with no merge, so `env={"KEY": "v"}` drops `PATH`. Docstring says `env` goes "as is" | Question: document "empty = inherit, non-empty = replace", or merge over `os.environ` | MEDIUM |
| 3 | 6, 7, 9 | `run_pool.py:211,235,295`: only `terminate()` is ever sent; a child that ignores SIGTERM holds its slot forever and survives shutdown | Question: add `kill()` after a timeout, or document that callers handle it | MEDIUM |
| 4 | 8 | `run_monitor.py:65`: `state.lines[-error_tail_lines:]` with `error_tail_lines=0` copies the whole log, not nothing | use `lines[len(lines)-n:]` guarded for 0 | LOW |
| 5 | 8 | `run_monitor.py:169`: a `run_filter` that raises aborts the tick at that run: later rows, the idle label (173) and row deletion (174-175) are skipped every tick until the filter stops raising; `ui.timer` reports it via `app.handle_exception` and keeps running | catch per run and treat as shown, or leave as is | LOW |
| 6 | Theme, Table | `table.py:106`, `theme.py:652`: `client.on_connect` only appends the handler (nicegui 3.18 `client.py:339-345`); handlers run in `handle_handshake` (`client.py:410-411`). A widget built after the handshake (event handler, async page after `await client.connected()`) restores only on a later reconnect | Confirmed by code (mechanism); a live check shows how often apps hit it. Fix: if `client.has_socket_connection`, run `_restore` now via `background_tasks.create` | LOW |
| 7 ✅ 2026-11-05 | Table | `table.py:95,112`: `storage_key` goes into JS source inside single quotes on both read and write (`removeItem`/`setItem`); only the stored value is `json.dumps`-escaped. A key with `'` breaks the call (developer-supplied, not user input) | `json.dumps(storage_key)` in all three places | LOW |
| 8 ✅ 2026-11-05 | 3, 6 | `run_pool.py:190-192,212-213`: any exception from `_execute` other than the three caught ones reaches `_finalize`, which turns `running` into `cancelled`, so a crash reads "cancelled by user". Concrete trigger: `submit([])` -> `TypeError` -> `state.argv[0]` raises `IndexError` inside the handler -> status `cancelled`, no log line, "Task exception was never retrieved" (reproduced) | reject empty `argv` in `submit`; in `_run_lifecycle` catch `Exception`, log it, append a log line, set `failed` before `_finalize` | LOW |
| 9 | 4, 5, 6, 7, 9 | `run_pool.py:197,211,235,295`: `terminate()` signals the direct child only, no process group (`start_new_session` / `killpg`). A grandchild that inherited stdout keeps `_pump_output` from seeing EOF: the run stays `running` and holds its slot after the child exits, and `request_cancel` returns `False` (`run_pool.py:237`) so Stop does nothing. On Stop of `sh -c "sleep 3; echo x"` the shell dies with -15 but the run ends only when `sleep` does (reproduced: `sh -c "sleep 3 & echo hi"` stays `running` with `returncode=0`, cancel -> `False`) | spawn with `start_new_session=True` and signal the group (`os.killpg`) in cancel, finalize and shutdown; together with #3 | MEDIUM |
| 10 | 8 | `run_monitor.py:132-134`: a new row pushes the whole `state.lines` into `ui.log` one `Label` at a time and `ui.log.push` then removes the overflow one by one; a page opened on a run with 100k lines builds and deletes ~100k elements in one tick | on a fresh view start `shown` at `max(0, len(lines) - log_max_lines)` | LOW |
| 11 | 8 | `run_monitor.py:133` + nicegui `elements/log.py:30`: `ui.log.push` splits on `splitlines()`, so a blank output line adds nothing and a line with `\r` (progress bars) adds several rows; the caption counts `state.lines`, so it and the DOM disagree | Question: push `line or " "`; leave `\r` as is or keep the text after the last `\r` | LOW |
| 12 | Table | `table.py:39-42` + `theme.py:150-153`: the first column gets `required` but also its `ic-p{priority}` class, so a `priority: 2/3` on it hides it by CSS; the docstring says it is never hidden | skip the priority class for column 0 | LOW |
| 13 | 8 | `run_monitor.py:71-82`: every Stop click builds a new `ui.dialog` that is closed, never deleted; dialogs pile up inside the row until the row is deleted | `dialog.on("hide", dialog.delete)` or build one dialog per row | LOW |

## Order of work

1. #1, #2, #3, #9, #8: all in `run_pool.py` (#3 and #9 share one kill path), add tests in `tests/test_run_pool.py`.
2. #4, #5, #10, #11, #13: `run_monitor.py`.
3. #6, #7, #12: fix in `table.py` / `theme.py`.

## Done when

- [ ] every finding has ✅ or a "keep as is" decision with a reason;
- [ ] Known gaps in the map lists every open HIGH and MEDIUM finding.
