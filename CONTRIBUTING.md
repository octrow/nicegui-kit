# Contributing

**English** | [Русский](CONTRIBUTING.ru.md)

Bug reports, fixes and small additions are welcome. For anything bigger than a bug fix, open an issue
first so we can agree on the API before you write it.

## Setup

```bash
git clone https://github.com/octrow/nicegui-kit && cd nicegui-kit
uv sync --extra dev
uv run pytest -q
uvx ruff check .
uv run python examples/showcase.py   # http://127.0.0.1:8787, ?dark=1 forces dark
```

## What the kit accepts

- A helper earns its place when at least two apps wrote it by hand. Show both in the issue.
- No hex colors or pixel values in helpers: use the tokens in `theme.py`. A new color token comes with
  its text/background pair in `theme.TEXT_PAIRS`, and the tests check it at WCAG AA in both themes.
- No Tailwind `gap-*` (NiceGUI #2171); spacing comes from the kit classes.
- `run_pool` stays free of `ui.*` calls.
- User-facing strings go into `texts.py`, in both `RU` and `EN`.
- Visual changes: add before/after screenshots of `examples/showcase.py` in light and dark to the PR.
  The design rules are in [DESIGN.md](DESIGN.md).
- Prose changes to README.md land in README.ru.md in the same PR (and the other way round).

## Commits

`<type>: <description>`, types `feat`, `fix`, `refactor`, `docs`, `test`, `chore`, `perf`, `ci`.

By contributing you agree that your code is released under the [MIT License](LICENSE) and that you
follow the [Code of Conduct](CODE_OF_CONDUCT.md).
