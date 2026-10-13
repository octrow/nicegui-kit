# Security policy

**English** | [Русский](SECURITY.ru.md)

## Supported versions

The latest release on PyPI gets fixes. Older versions don't.

## Reporting a vulnerability

Report it privately through
[GitHub security advisories](https://github.com/octrow/nicegui-kit/security/advisories/new), not in a
public issue. Include the version, what an attacker can do, and steps or code to reproduce. You'll get a
reply within a week.

The kit runs subprocesses (`run_pool`) and renders text into pages, so the most relevant reports are
command injection through `submit()` arguments and HTML injection through kit helpers. `run_pool` passes
`argv` as a list and never uses a shell; the command itself is chosen by the app, not the kit.
