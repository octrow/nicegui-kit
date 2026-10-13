---
name: nicegui-kit-gui
description: Build, extend, migrate or review a NiceGUI browser GUI for a Python project using nicegui-kit (theme, layout helpers, subprocess run pool and live run monitor). Use whenever a project needs a GUI/dashboard/form page or a screen that runs subprocesses with a live log, or the user says "на нашем kit", nicegui, nicegui-kit, ui.page.
---

# GUIs on NiceGUI + nicegui-kit

The kit (https://github.com/octrow/nicegui-kit, `pip install nicegui-kit`) is the only source of truth for look and patterns:

- `examples/showcase.py` — the living reference (header + nav, filters, form dialog, run monitor,
  component gallery). Mirror its structure.
- `docs/api.md` — the API (`theme`, `layout`, `table`, `hotkeys`, `run_pool`, `run_monitor`);
  check signatures in `src/nicegui_kit/*.py` when in doubt.

## Wiring

```toml
[project]
dependencies = ["nicegui-kit"]
[tool.pytest.ini_options]
asyncio_mode = "auto"   # dev deps: pytest, pytest-asyncio
```

`tests/conftest.py`: `pytest_plugins = ["nicegui.testing.user_plugin"]`.

## Rules that aren't obvious from the code

- `theme.apply_theme()` once before `ui.run()`; no project colors/fonts/CSS, no hex or px in pages.
- No Tailwind `gap-*` (NiceGUI #2171): kit classes or `style("gap: var(--ic-s3)")`.
- Subprocesses only via `run_pool.submit` + `run_monitor.attach_run_monitor`; no `ui.*` in `on_line`.
- Shutdown: `app.on_shutdown` passes `App` to one-arg handlers — wrap:
  `async def _stop(): await run_pool.terminate_all_live_processes()`.
- `ui.run(host="127.0.0.1", reload=False, language="ru")` under
  `if __name__ in {"__main__", "__mp_main__"}:` (reload would drop run_pool state).
- Quasar's `!important` is layered and beats yours: style children, pass a color class via props,
  or `color=None` on `ui.button`. `ui.label` has no `.nicegui-label` class.
- `ui.log` is a QScrollArea — it needs an explicit height.
- `heading(level=3)` renders as a small uppercase group label, not a card title — use level 2.
- Russian UI copy, sentence case, verbs on buttons; one `primary` button per screen, `danger`
  behind a confirmation dialog.

## Tests

`nicegui.testing.User` per page (`@pytest.mark.nicegui_main_file(path)`). That file runs via
runpy outside its package: use absolute imports there. Test data only under `tmp_path`.
Headless screenshots don't wait for `ui.timer` data — an empty list there isn't a bug.
