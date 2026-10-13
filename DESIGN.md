---
name: nicegui-kit
description: Shared NiceGUI theme + layout for instrumental pet-project GUIs — one accent, AA contrast, offline Inter Variable.
colors:
  accent-100: "#DEF3FA"
  accent-300: "#99CEDF"
  accent-600: "#20758C"
  accent-700: "#0A6175"
  accent-800: "#004C5D"
  canvas: "#F3F6F8"
  surface: "#FFFFFF"
  surface-sunken: "#EEF3F4"
  border: "#D8DDDF"
  border-strong: "#C6CED0"
  text: "#262E31"
  text-secondary: "#535D60"
  text-muted: "#646E72"
  status-running: "#845510"
  status-ok: "#1C6E42"
  status-error: "#A8372E"
  status-idle: "#5B6569"
  warn-bg: "#FEF5E8"
  warn-border: "#D9B070"
  warn-ink: "#684807"
  fail-bg: "#FEF3F1"
  fail-border: "#F8A59B"
  fail-ink: "#6C1614"
  fail-body: "#881A19"
  dark: "#262E31"
  dark-page: "#171D1F"
typography:
  title-page:
    fontFamily: "var(--ic-sans)"
    fontSize: "1.75rem"
    fontWeight: 650
    lineHeight: 1.2
    letterSpacing: "-0.02em"
  title-section:
    fontFamily: "var(--ic-sans)"
    fontSize: "1.125rem"
    fontWeight: 600
    lineHeight: 1.35
    letterSpacing: "-0.006em"
  status:
    fontFamily: "var(--ic-sans)"
    fontSize: "1rem"
    fontWeight: 600
    lineHeight: 1.4
    letterSpacing: "0.004em"
  meta:
    fontFamily: "var(--ic-sans)"
    fontSize: "0.875rem"
    fontWeight: 500
    lineHeight: 1.45
    letterSpacing: "0.005em"
  mono:
    fontFamily: "var(--ic-mono)"
    fontSize: "0.875rem"
    lineHeight: 1.5
  body:
    fontFamily: "var(--ic-sans)"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.5
rounded:
  chip: "999px"
  banner: "4px"
  focus-ring: "4px"
  code: "3px"
spacing:
  group: "1rem"
  section: "1.5rem"
components:
  button-default:
    backgroundColor: "{colors.accent-600}"
    textColor: "#FFFFFF"
    typography: "{typography.meta}"
    padding: "0 16px"
  status-running:
    textColor: "{colors.status-running}"
  status-ok:
    textColor: "{colors.status-ok}"
  status-error:
    textColor: "{colors.status-error}"
  status-idle:
    textColor: "{colors.status-idle}"
  chip-neutral:
    backgroundColor: "{colors.surface-sunken}"
    textColor: "{colors.text-secondary}"
    rounded: "{rounded.chip}"
  banner-warning:
    backgroundColor: "{colors.warn-bg}"
    textColor: "{colors.warn-ink}"
    rounded: "{rounded.banner}"
  failure-card:
    backgroundColor: "{colors.fail-bg}"
    textColor: "{colors.fail-ink}"
---

# Design System: nicegui-kit

## Overview

nicegui-kit is not a brand — it is the shared visual contract for a family of small, single-operator, browser-served tools (job runners, scrapers, review queues and other pet projects), extracted from an internal job-runner GUI. Its stated goal is GUIs that are "быстро, просто, симпатично" (fast, simple, pleasant) — nothing more decorative is claimed, and nothing beyond what is implemented in `theme.py`/`layout.py`/`run_monitor.py` is asserted here.

The default posture is **Operate, not Explore**: light and dark themes from one token dict (`theme.TOKENS`; `theme_toggle()` cycles system → light → dark and remembers the choice in localStorage), instrumental UI for running and watching background jobs (subprocess pools, queues, logs), one author-chosen accent color, and mandatory Cyrillic support (Russian is the default UI language; every kit string lives in `texts.TEXTS`, and `texts.TEXTS.update(texts.EN)` switches the kit to English at call time). Every text/background pairing listed in `theme.TEXT_PAIRS` is checked at WCAG AA (4.5:1) in both themes by `tests/test_theme_layout.py`; Quasar defaults that fail AA are replaced.

**Key characteristics:**
- One accent color (teal-petrol, OKLCH 0.525 0.085 220 authored as `#20758C`), not a multi-color brand palette.
- Flat surfaces, tonal layering instead of shadows (`box-shadow: none` on cards); only floating layers (menus, dialogs) cast a soft shadow.
- One spacing scale (`theme.SIZES`: 4/8/12/16/24/32 px, control heights 40/28) exposed as `--ic-*` variables; helpers never use Tailwind `gap-*` (NiceGUI #2171).
- A fixed 16px type floor that overrides Quasar's 14px default, because Quasar's defaults under-serve Cyrillic legibility.
- Self-hosted, offline-first typography (Inter Variable) with an explicit Cyrillic-safe system-font fallback chain.
- A 4-status color vocabulary (running/ok/cancel/error/idle) reused identically across every consumer app via `run_monitor`.

## Colors

The palette is one authored accent plus a neutral scale plus a small status vocabulary — there is no secondary or tertiary brand color.

### Primary
- **Accent 600** (`#20758C`): buttons, links (700-weight variant), focus rings, active states. Authored in OKLCH as `0.525 0.085 220` (deep teal-petrol) to replace Quasar's default blue.
- **Accent 700** (`#0A6175`): link color and hover-ink; `info` role uses this too (the code comment notes Quasar's default cyan info color fails AA, so `info == accent`).
- **Accent 800** (`#004C5D`): link hover state (darkest step).
- **Accent 300** (`#99CEDF`): link underline color, `::selection` companion tone.
- **Accent 100** (`#DEF3FA`): `::selection` background.

### Neutral
- **Canvas** (`#F3F6F8`): page background (`body`, `.q-page`, `.nicegui-content`).
- **Surface** (`#FFFFFF`): card background.
- **Surface Sunken** (`#EEF3F4`): recessed density surfaces — log panels (`.nicegui-log`), inline `<code>` background.
- **Border** (`#D8DDDF`): default card/log border.
- **Border Strong** (`#C6CED0`): chip border, filter-bar toggle border.
- **Text** (`#262E31`): primary ink; doubles as the `dark` role color.
- **Text Secondary** (`#535D60`): secondary/flat control ink; doubles as the `secondary` role color.
- **Text Muted** (`#646E72`, darkened from `#687276`: the old value read at 4.41:1 on the sunken log surface): reassurance copy (`.ic-reassure`), quiet diagnostics (`.ic-diag-ok`); also the `idle` status color.
- **Dark theme**: every token above has a dark twin in `TOKENS["dark"]` (canvas `#13191B`, surface `#1B2326`, sunken `#222B2E`, text `#E4EAEC`, accent-600 `#5FB8CF`). The accent is re-authored lighter so it reads on a dark canvas; filled controls take `on-fill` ink (white in light, canvas in dark) instead of Quasar's fixed white. Quasar's brand roles (`primary`, `negative`, `dark`, `dark_page`, …) point at the `--ic-*` variables, so `color=primary` follows the theme.

### Status vocabulary (not decorative color — semantic state)
- **Running** (`#845510`, darkened from `#8F5D14` so it also reads on its own badge tint): an in-progress run. Class `.ic-status--running`.
- **Ok** (`#1C6E42`, darkened from `#207748`, same reason): a completed/successful run. Class `.ic-status--ok`; also the Quasar `positive` role.
- **Error** (`#A8372E` for status text / `#A02A26` for the Quasar `negative` role, 6.46:1 / 7.36:1): a failed run. Class `.ic-status--error`.
- **Idle / Cancel** (`#5B6569`): queued-but-inactive, or user-cancelled. Classes `.ic-status--idle`, `.ic-status--cancel`.
- **Warning** (`#835D13` Quasar role / `#684807` banner ink, 5.93:1): the code comment notes Quasar's default warning color fails AA, hence the override.

Status words in lists render as badges (`.ic-badge` + `ic-status--*`): the status ink on a 10% tint of itself; `tests/test_theme_layout.py` holds every status at AA on its tint over surface, canvas and sunken, in both themes.

### Named Rules
**The One-Accent Rule.** There is exactly one brand accent (`accent-600`/`700`/`800`); everything else is neutral gray or a semantic status color. No second decorative hue exists in the stylesheet.

**The AA-Or-Replace Rule.** Where Quasar's own default role color (`info`, `warning`) failed AA contrast on white, the kit replaces it rather than keeping the framework default — documented inline in `theme.py` for `info` and `warning`.

## Typography

**Body font:** `InterVariable` (self-hosted `assets/fonts/InterVariable.woff2`, SIL OFL 1.1), falling back to `"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI Variable Text", "Segoe UI", Roboto, "Noto Sans", "Liberation Sans", "DejaVu Sans", Arial, sans-serif` — a stack chosen to stay Cyrillic-safe when the variable font file is absent (`FONT_FILE.is_file()` gates whether `@font-face` is even injected).
**Mono font:** `ui-monospace, "SF Mono", "Cascadia Mono", "Segoe UI Mono", "JetBrains Mono", Consolas, "DejaVu Sans Mono", "Liberation Mono", "Noto Sans Mono", "Courier New", monospace` — used for logs, inline code, and CLI command display.

**Character:** an instrumental, information-dense pairing: a 16px body floor (deliberately raised above Quasar's 14px default), tabular numerals on status/meta text, and ligature-free mono for logs so nothing visually merges.

### Hierarchy (role classes, all in `theme.py`)
- **`t-title-page`** (weight 650, 1.75rem/1.2, -0.02em): page-level `<h1>`, set via `layout.heading(text, level=1)`.
- **`t-title-section`** (weight 600, 1.125rem/1.35, -0.006em): section-level `<h2>`, via `layout.heading(text, level=2)`.
- **`t-status`** (weight 600, 1rem/1.4, tabular-nums): run status lines in `run_monitor` (e.g. "идёт", "готово", "ошибка, код возврата N").
- **`t-meta`** (weight 500, 0.875rem/1.45, tabular-nums, `text-secondary` ink): secondary metadata text.
- **`t-title-group`** (weight 600, 0.8125rem, +0.04em, uppercase, `text-secondary`): group label `<h3>`, via `layout.heading(text, level=3)`.
- **`t-muted`**: quiet copy (empty states). **`t-brand`**: the app name in a header.
- **`t-mono`** (0.875rem/1.5, no ligatures, `overflow-wrap: anywhere`): general monospace text blocks.
- **`t-log`** (inherits mono sizing, `white-space: pre-wrap`): the live run log surface inside `.nicegui-log`.
- **`.q-btn` label** (weight 600, 0.9375rem, `text-transform: none`): the code comment notes Quasar's default all-caps button labels are overridden because "Russian labels suffer" under text-transform: uppercase.
- **Markdown body (`.md-body`)** carries its own smaller sub-scale: `h1` 1.1875rem/650, `h2` 1.0625rem/620, `h3`–`h6` 1rem/600–650, body text at the 1rem/1.65 base, all content lines capped at `max-width: 68ch`.

### Named Rules
**The 16px Floor Rule.** `html { font-size: 100% }` plus explicit `1rem` on every form/field/label class exists specifically to override Quasar's 14px body default — stated in the code as needed for Cyrillic legibility, not an aesthetic preference.

**No-Shout Rule.** Button labels are never uppercased (`text-transform: none` overrides Quasar's default), because the kit is Russian-first and uppercase Cyrillic reads worse than uppercase Latin.

## Layout

Every page places all of its content inside exactly one `layout.page_container()`: a centered column (`.ic-page`), 24px padding (16px under 600px), capped at one of two widths — `PAGE_MAX_WIDTH_FORM` (`max-w-4xl`, form-shaped pages) or `PAGE_MAX_WIDTH_WIDE` (`max-w-6xl`, dashboard/monitor pages). `page_container()` also zeroes NiceGUI's own `.nicegui-content` padding/gap so the kit's own rhythm is the only spacing applied.

Spacing comes from `theme.SIZES` (`--ic-s1`…`--ic-s8`) through classes, never from Tailwind `gap-*` (NiceGUI #2171, unreliable on Ubuntu):
- `.ic-page` — 24px between sections; `.ic-card` — 16px inside a card (`section_card()`); `.ic-stack` — 8px between list items; `.ic-actions` — right-aligned buttons, 8px apart (`actions_row()`); `.ic-state` — one status line (`empty`/`waiting`/`failed`), never wraps its icon away from its words; `.ic-split` — label left, control right.

`section_card(recessive=True)` sits back: `surface-sunken` background, no border.

The filter-bar convention (`.ic-filters`) fixes one control height (`min-height: 40px`) across toggle/select/search controls so a mixed row of controls lines up, and forces controls to full width and toggle segments to `flex: 1` under 700px so a stacked filter bar never shows three different widths.

Markdown tables (`.md-body table`) scroll horizontally (`overflow-x: auto`) rather than wrapping, and cell content does not word-break (`overflow-wrap: normal`) so IDs/UUIDs stay intact — an explicit trade-off noted in the code ("scroll, don't shred uuids").

## Elevation & Depth

The kit is flat by design: `.q-card { box-shadow: none; }` explicitly strips Quasar's default card shadow. Depth is conveyed entirely through **tonal layering** — three background steps (`canvas` → `surface` → `surface-sunken`) plus 1px borders (`border` / `border-strong`), never through shadow.

### Named Rules
**The Flat-By-Default Rule.** No component in this kit uses `box-shadow` for elevation. Layering is expressed as canvas/surface/sunken background steps plus borders, not shadow.

## Shapes

Radius is used sparingly and only where the code sets it explicitly:
- **Focus outline**: `border-radius: 4px` on `:focus-visible`.
- **Warning banner**: `border-radius: 4px` (`.ic-banner`).
- **Inline code**: `border-radius: 3px` (`.md-body code`).
- **Chips**: fully pill-shaped, `border-radius: 999px` (`.ic-chip`).
- **Cards, run rows** (`.ic-run`): 8px. **Log panels, code blocks**: 6px.

Buttons keep Quasar's own radius.

## Components

### Buttons
- **Shape:** Quasar default radius (kit does not override button radius).
- **Label:** 0.9375rem, weight 600, `letter-spacing: 0.01em`, never uppercased (see Typography Named Rules).
- **One way to make a button:** `layout.button(text, kind=, size=)`. Kinds: `primary` (filled, one per screen), `normal` (outline), `quiet` (flat), `danger` (outline in `negative`, stands apart after `ui.space()`). Sizes: `ctl` (40px, as tall as a field) and `row` (28px, inside a list row).
- **Destructive action:** `kind="danger"` (e.g. "Остановить" in `run_monitor`), always behind a confirmation dialog (`_confirm_cancel`) — the kit never lets a destructive action fire on a single click.
- **Disabled:** Quasar default (60% opacity; its layered `!important` is not worth fighting).

### Chips
- **Style:** pill shape (999px radius), 12px/18px text, weight 600, 1px border.
- **Neutral variant:** `surface-sunken` background, `border-strong` border, `text-secondary` ink (`.ic-chip--neutral`) — currently the only variant shipped; the README notes it is unused unless a consuming app renders one.

### Cards / Containers
- **Corner style:** 8px.
- **Background:** `surface`.
- **Shadow strategy:** none — see Elevation & Depth.
- **Border:** 1px `border` (`#D8DDDF`).
- **Internal padding:** 16px, 16px between blocks (`.ic-card`).

### Banners / Failure Cards
- **Warning banner** (`.ic-banner`): `warn-bg` background, `warn-border` 1px border, `warn-ink` text, 4px radius.
- **Failure card** (`.ic-failure`): `fail-bg` background, `fail-border` 1px border; title in `fail-ink`, body copy in `fail-body`. Kept for apps that render one; `run_monitor` no longer does (it said the failure three times and printed the log twice).
- **Reassurance text** (`.ic-reassure`): `text-muted`, 13px, weight 400 — deliberately quiet, used for non-blocking notices.
- **Diagnostics**: `.ic-diag-ok` is `text-muted` (quiet — nothing wrong); `.ic-diag-warn` is `warn-ink` at weight 500 (a warning, never a hard block) — codified in the comment "ok is quiet, not-ok warns (never blocks)".

### States (empty / waiting / failed)
- **Wide data tables: one value per column, one line per row** (`table.py`). On a wide screen show the columns as they are: dense rows and numbers in their own sortable columns read faster than merged cells (repo-scout's two-line `"sub"` cells were tried and reverted: half the rows per screen, numbers no longer comparable). On a narrow window `"priority": 2|3` columns hide by container width (80rem / 56rem), text cells are capped at 30% of the table, and the row's detail panel shows every field. `column_picker()` lets the user choose. `"sub"` is for truly secondary text only, never for a second number.
- **`layout.empty(text, action=None)`**: `t-muted` words saying what will appear, plus at most one quiet button that makes it appear. `table.empty_aware_table` uses the same ink.
- **`layout.waiting(text)`**: a primary-colored spinner beside `t-meta` words.
- **`layout.failed(text, retry=None)`**: error icon + error ink (never color alone), the problem and the recovery in plain words, an optional "Повторить". No traces, no internal names.

### Inputs / Fields
- **Style:** Quasar defaults for stroke/background/radius; the kit only overrides font-family/size (1rem/1.5 line-height) and focus-state border color.
- **Focus:** field focus border switches to `accent-600` (`.q-field--focused .q-field__control:after`); page-wide `:focus-visible` gets a 2px `accent-600` outline with 2px offset and 4px radius.

### Links, Focus, Selection
- **Links:** `accent-700` ink, underline colored `accent-300` (not the link's own ink color — a lighter, quieter underline).
- **Link hover:** `accent-800` ink, underline switches to `currentColor`.
- **Focus-visible:** 2px solid `accent-600` outline, 2px offset, 4px corner radius — applied globally, not just to interactive-looking elements.
- **Text selection:** `accent-100` background, `text` (`#262E31`) foreground — never the accent ink color, to keep selected body copy readable.

### Run Monitor (signature component)
`run_monitor.attach_run_monitor()` renders a live list of subprocess runs against 5 states (`queued`, `running`, `done`, `cancelled`, `failed`, mapped to the 4 status CSS classes above — `cancelled` reuses the idle color). Each run is an expandable row (`ui.expansion`, `.ic-run`) whose header is columns: name (grows, ellipsis) · status badge (`.ic-badge`) · duration (`.ic-run-time`, fixed min-width), so status and time line up across rows and the state is said exactly once. Inside: one log panel (`.ic-log-panel`, sunken) with a header bar — «Вывод: N строк» left; cancel (danger, behind a confirmation dialog, while pending) and an icon-only copy button (tooltip + aria-label «Скопировать для чата»: summary + last 15 lines) right — then a borderless `ui.log` whose height follows its lines up to `LOG_VISIBLE_LINES` (14, via `--ic-log-lines`) and scrolls after that; capped at 2000 DOM lines. The governing invariant, stated in the module docstring: the poll timer (`ui.timer`, 1s default) **never rebuilds** an existing run's widgets, it only mutates label text/classes and pushes new log lines — because NiceGUI has no virtual DOM, and a rebuild would silently reset expansion open/closed state, log scroll position, and focus.

### Markdown Reading Surface (`.md-body`)
A dedicated typographic mode for rendered markdown/docs content, distinct from the UI's control typography: 1rem/1.65 body line-height (looser than the 1rem/1.5 UI default, for prose readability), headings on the shared type scale (`fs-md`, `fs-base`), all block content capped at `--ic-measure` (68ch), tables forced to horizontal scroll rather than wrap, and inline `code` on a `surface-sunken` chip with `--ic-r-sm` radius.

## 2026 baseline: what the kit guarantees

| Area | In the kit |
|---|---|
| Column layouts | `layout.grid()`: 12 columns, kit gutter (24px; 16px on touch), children `.classes("ic-span-N")`, everything full width under 700px. `grid(min_col="18rem")`: intrinsic auto-fill grid with no spans. One content column per page (`page_container`, `max-w-4xl` / `max-w-6xl`). |
| Spacing & sizing | `theme.SIZES`: 4-px base, steps 4/8/12/16/24/32, control heights 40/28 (44/36 under `pointer: coarse`, WCAG 2.2 target size). Only `--ic-*` variables; no Tailwind `gap-*`. |
| Font system | Inter Variable, self-hosted, one file, `wght` 100–900 + optical sizing; Cyrillic-safe fallback stack; tabular numerals on data; ligature-free mono for logs. |
| Scale & hierarchy | `theme.TYPE_SCALE` (rem): xs .8125 · sm .875 · ui .9375 · base 1 · md 1.125 · lg 1.375 · xl 1.75. Weights `theme.WEIGHTS` (400/500/600/650), leading `theme.LEADING` (1.2/1.35/1.45/1.5/1.65), tracking `theme.TRACKING`. Every role class reads these variables. 16px body floor. |
| Corners, elevation, measures | `theme.RADII` (4/6/8/pill), `theme.SHADOWS` (menu, dialog only), `theme.MEASURES` (68ch reading width, dialog/select/grid-column minimums). |
| Color & tokens | `theme.TOKENS` light/dark, semantic names (canvas/surface/text/status), Quasar roles bound to the tokens, `TEXT_PAIRS` held at AA by tests. |
| Component states | default / hover / focus-visible (2px accent ring) / active (1px press) / disabled / loading (`waiting`) / empty (`empty`) / error (`failed`, field error) / success (positive toast). |
| Motion | `theme.MOTION`: 120 / 200 / 320 ms, `ease-out` cubic-bezier(.16,1,.3,1); color/border/press transitions only, `.ic-appear` for one entrance; `prefers-reduced-motion` disables all of it. |
| Structure | header → one content column → create/edit card → the list it feeds, with its filters right above it. Forms end in `actions_row(end=False)` (primary on the fields' left edge, first); dialogs end in `actions_row()` (right). One primary button per screen; danger buttons stand apart and confirm. No frame inside a frame: inner panels are tonal fills, not more borders. |
| State & validation | `layout.field(...)`: label always on top (`stack-label`, never read as a placeholder), hint below, error replaces hint. Validate on blur, re-check on every keystroke once an error shows, `required` = rule + visible `*` + `aria-required`. Error text names the field and the fix. |
| Autocomplete & keyboards | `FIELD_KINDS` sets `type` / `inputmode` / `autocomplete` / `enterkeyhint` (email, tel, url, search, number, integer, one-time code, current/new password); `suggestions=` gives inline completion; password fields have a show toggle. |
| Accessibility & microcopy | Real h1–h3, AA contrast in both themes, focus ring on everything, `.ic-sr-only`, `scroll-margin` for anchors, theme toggle with aria-label + tooltip. Copy: buttons are verbs ("Запустить", "Повторить"), empty states say what will appear and how, errors say what broke and what to do, no internal names or traces. |

## Do's and Don'ts

### Do:
- **Do** keep exactly one accent color (`accent-600`/`700`/`800`); every other color is neutral or a semantic status color.
- **Do** gate every destructive action (cancel/stop) behind a confirmation dialog, per `run_monitor._confirm_cancel`.
- **Do** mutate existing run-monitor widgets on each poll tick rather than rebuilding them — rebuilding destroys expansion/scroll/focus state (stated invariant in `run_monitor.py`'s module docstring).
- **Do** keep the 16px body-text floor; do not let a form field, label, or button fall back to Quasar's 14px default.
- **Do** keep all four status colors (running/ok/error/idle+cancel) at their documented AA contrast ratios on white ( ≥4.5:1); don't swap in a fifth ad hoc status color without measuring and documenting its ratio.
- **Do** treat Russian/Cyrillic as the primary language target for every typographic decision (no uppercase transforms, generous line-height, a Cyrillic-safe font fallback chain).

### Don't:
- **Don't** add `box-shadow` for elevation — depth is tonal layering (canvas/surface/surface-sunken) plus borders only.
- **Don't** introduce a second brand accent hue; secondary/tertiary color roles do not exist in this system.
- **Don't** rename the `ic-`/`t-`/`md-body` CSS class prefixes — the README states this explicitly is pure-diff-noise-avoidance, kept from the original source on purpose.
- **Don't** reintroduce Quasar's default uppercase button labels or its default `info`/`warning` role colors — both were replaced for documented AA-contrast and Cyrillic-readability reasons.
- **Don't** write a hex color or px size in a page: add a token to `TOKENS`/`SIZES` (both themes, plus a `TEXT_PAIRS` entry if it carries text) and the contrast test guards it.
- **Do** guard app CSS the way the kit guards its own: `assert theme.raw_values(APP_CSS) == []` fails on any literal weight, leading, tracking, radius, shadow, font size, rem/px gap or color (em and 1–2px hairlines are allowed).
- **Don't** use Tailwind `gap-*` classes; use the kit's layout classes or an inline `style("gap: …")`.
