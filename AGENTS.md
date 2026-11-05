# Agents: start here

1. `README.md` and `DESIGN.md`: what the kit is and its design rules.
2. `docs/logic-map.md`: how a command line becomes a finished run (pool, monitor), plus the theme, layout, table and hotkeys helpers: every step, every branch, the module behind it.
3. `docs/plans/`: `2026-11-05-logic-map-fixes.md` lists the known logic gaps.
4. Open bugs, plans and ideas: [PLAN.md](PLAN.md).

Rules:
- Change a step or a branch in `src/nicegui_kit` -> update `docs/logic-map.md` in the same commit.
- `tests/test_logic_map.py` fails when a `Module:` line in the map points to a module that is gone.
