# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions follow
[Semantic Versioning](https://semver.org/).

## [0.1.3] - 2026-10-15

### Changed

- README images get phone-width variants, so text stays readable on a 390px screen.

## [0.1.2] - 2026-10-15

### Changed

- README redesign: light/dark SVG hero and diagram, badges; images use absolute URLs so they render on PyPI.

## [0.1.1] - 2026-10-15

### Fixed

- `run_monitor`: clearing a filter no longer moves the runs it had hidden to the end of the list; a filter
  now hides runs in place, and their open log and scroll position survive it.

## [0.1.0] - 2026-10-14

First public release.

### Added

- `theme`: light and dark tokens with every text/background pair tested at WCAG AA, self-hosted Inter
  Variable, `theme_toggle()` (system → light → dark, remembered), type scale, motion and touch-size tokens.
- `layout`: `page_container`, `heading`, `section_card`, `grid`, `field`, `search_field`, `filter_bar`,
  `actions_row`, `button`, `empty` / `waiting` / `failed`, `markdown_reader`, `copy_for_chat_button`.
- `table.empty_aware_table()`: a table and its "nothing found" label kept in sync.
- `hotkeys.on_keydown()`: page hotkeys that ignore keyup, modifiers and typing in inputs.
- `texts`: every kit string in one dict, Russian by default, English via `texts.EN`.
- `run_pool`: subprocess pool with slots, a queue cap, cancel and graceful shutdown.
- `run_monitor.attach_run_monitor()`: live list of runs with status, log and cancel.
- `examples/showcase.py`: a sample job runner screen and a component gallery.
- Agent skill `nicegui-kit-gui` for Claude Code and other coding agents.

[0.1.3]: https://github.com/octrow/nicegui-kit/releases/tag/v0.1.3
[0.1.2]: https://github.com/octrow/nicegui-kit/releases/tag/v0.1.2
[0.1.1]: https://github.com/octrow/nicegui-kit/releases/tag/v0.1.1
[0.1.0]: https://github.com/octrow/nicegui-kit/releases/tag/v0.1.0
