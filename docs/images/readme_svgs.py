"""Builds the README SVGs from the kit's own tokens and limits, so they follow theme.py.

    uv run python docs/images/readme_svgs.py
"""

from dataclasses import dataclass
from pathlib import Path

from nicegui_kit import run_pool, theme

OUT = Path(__file__).parent
W = 1200
SANS = "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
R = theme.RADII["r-lg"]
HERO_H = 490
FLOW_H, FLOW_GAP, BOX_Y, BOX_H = 308, 26, 56, 196
BOX_W = (W - 128 - 3 * FLOW_GAP) / 4
# chip fills: the kit draws these with color-mix() in CSS, which an SVG image can't use
CHIP_BG = {"light": {"ok": "#E3F2E9", "err": "#FBE4E1"}, "dark": {"ok": "#1D3428", "err": "#3A2220"}}


@dataclass(frozen=True)
class Chip:
    text: str
    role: str  # "ok" | "err": token for the ink, CHIP_BG key for the fill
    width: float


@dataclass(frozen=True)
class Step:
    title: str
    code: str
    lines: tuple[str, ...]


STEPS = (
    Step("Your page", "submit(argv)", ("a button or a timer", "decides what to run")),
    Step("Run pool", "run_pool", (f"{run_pool.MAX_PARALLEL_RUNS} running at once,",
                                  f"{run_pool.MAX_TOTAL_PENDING} queued at most,", "cancel kills the process")),
    Step("Subprocess", "on_line(line)", ("no shell, argv as a list,", "stdout + stderr merged,",
                                         f"lines up to {run_pool.STREAM_LINE_LIMIT // 2**20} MiB")),
    Step("Run monitor", "attach_run_monitor()", ("polls once a second,", "edits widgets in place,",
                                                 "so scroll stays put")),
)


def _luminance(hex_color: str) -> float:
    c = [int(hex_color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    c = [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def _ratio(fg: str, bg: str) -> float:
    a, b = sorted((_luminance(fg), _luminance(bg)), reverse=True)
    return (a + 0.05) / (b + 0.05)


def _min_ratio(name: str) -> float:
    t = theme.TOKENS[name]
    return min(_ratio(t[f], t[b]) for f, b in theme.TEXT_PAIRS)


def hero() -> str:
    light, dark = theme.TOKENS["light"], theme.TOKENS["dark"]
    seam = W / 2
    note = (f"{len(theme.TEXT_PAIRS)} text/background pairs per theme, tested at WCAG AA · "
            f"lowest {_min_ratio('light'):.2f}:1 light, {_min_ratio('dark'):.2f}:1 dark")
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{HERO_H}" viewBox="0 0 {W} {HERO_H}" role="img" aria-labelledby="t d">
<title id="t">nicegui-kit</title>
<desc id="d">The same run list drawn with the kit's light tokens on the left half and its dark tokens on the right half. {note}.</desc>
<defs>
<clipPath id="l"><rect width="{seam}" height="{HERO_H}"/></clipPath>
<clipPath id="r"><rect x="{seam}" width="{seam}" height="{HERO_H}"/></clipPath>
<clipPath id="all"><rect width="{W}" height="{HERO_H}" rx="16"/></clipPath>
</defs>
<g clip-path="url(#all)" font-family="{SANS}">
<g clip-path="url(#l)">{_scene("light")}</g>
<g clip-path="url(#r)">{_scene("dark")}</g>
<line x1="{seam}" y1="0" x2="{seam}" y2="{HERO_H}" stroke="{light["accent-600"]}" stroke-width="2"/>
<text x="{seam - 14}" y="70" text-anchor="end" font-family="{MONO}" font-size="18" fill="{light["accent-700"]}">light</text>
<text x="{seam + 14}" y="70" font-family="{MONO}" font-size="18" fill="{dark["accent-700"]}">dark</text>
<text x="1136" y="70" text-anchor="end" font-family="{MONO}" font-size="18" fill="{dark["text-muted"]}">one token dict</text>
</g>
</svg>
'''


def _scene(name: str) -> str:
    """Everything that changes with the theme: canvas, title, run list, contrast note."""
    t = theme.TOKENS[name]
    return (f'<rect width="{W}" height="{HERO_H}" fill="{t["canvas"]}"/>'
            + _title(t) + _run_rows(name) + _contrast_note(name))


def _title(t: dict[str, str]) -> str:
    return (
        f'<text x="64" y="70" font-family="{MONO}" font-size="18" fill="{t["text-muted"]}">'
        f'NiceGUI · Python ≥3.12 · MIT</text>'
        f'<text x="62" y="138" font-size="68" font-weight="700" letter-spacing="-1.5" fill="{t["text"]}">'
        f'nicegui-kit</text>'
        f'<text x="64" y="186" font-size="26" fill="{t["text-secondary"]}">'
        f'A light and dark theme, layout helpers and a subprocess pool with a live log</text>'
        f'<text x="64" y="218" font-size="26" fill="{t["text-secondary"]}">'
        f'for NiceGUI tools that run jobs.</text>'
    )


def _run_rows(name: str) -> str:
    t = theme.TOKENS[name]
    card = f'rx="{R}" fill="{t["surface"]}" stroke="{t["border"]}"'
    return (
        f'<rect x="64" y="262" width="1072" height="56" {card}/>'
        f'<text x="88" y="298" font-size="22" font-weight="600" fill="{t["text"]}">Nightly scrape</text>'
        + _chip(name, 930, 275, Chip("done", "ok", 76))
        + f'<text x="1036" y="297" font-size="20" fill="{t["text-secondary"]}">0:02</text>'
        f'<rect x="64" y="330" width="1072" height="88" {card}/>'
        f'<text x="88" y="366" font-size="22" font-weight="600" fill="{t["text"]}">Trial run</text>'
        + _chip(name, 870, 343, Chip("error · code 3", "err", 136))
        + f'<text x="1036" y="365" font-size="20" fill="{t["text-secondary"]}">0:00</text>'
        f'<rect x="80" y="380" width="1040" height="28" rx="{theme.RADII["r-sm"]}" fill="{t["surface-sunken"]}"/>'
        f'<text x="96" y="400" font-family="{MONO}" font-size="18" fill="{t["text"]}">start · boom</text>'
    )


def _chip(name: str, x: float, y: float, chip: Chip) -> str:
    ink, bg = theme.TOKENS[name][chip.role], CHIP_BG[name][chip.role]
    return (f'<rect x="{x}" y="{y}" width="{chip.width}" height="30" rx="15" fill="{bg}"/>'
            f'<text x="{x + chip.width / 2}" y="{y + 21}" text-anchor="middle" font-size="18" '
            f'font-weight="600" fill="{ink}">{chip.text}</text>')


def _contrast_note(name: str) -> str:
    """Each half states its own lowest pair, aligned to its outer edge."""
    left = name == "light"
    return (f'<text x="{64 if left else 1136}" y="458" font-family="{MONO}" font-size="18" '
            f'text-anchor="{"start" if left else "end"}" fill="{theme.TOKENS[name]["text-muted"]}">'
            f'{len(theme.TEXT_PAIRS)} text pairs · all ≥ 4.5:1 · lowest {_min_ratio(name):.2f}:1</text>')


def flow(name: str) -> str:
    t = theme.TOKENS[name]
    parts = []
    for i, step in enumerate(STEPS):
        x = 64 + i * (BOX_W + FLOW_GAP)
        parts.append(_box(t, x, step))
        if i:
            parts.append(_arrow(t, x))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{FLOW_H}" viewBox="0 0 {W} {FLOW_H}" role="img" aria-labelledby="t d">
<title id="t">How a run flows through nicegui-kit</title>
<desc id="d">Your page calls run_pool.submit with an argv list; the pool runs up to {run_pool.MAX_PARALLEL_RUNS} subprocesses and queues up to {run_pool.MAX_TOTAL_PENDING}; each output line goes to on_line; the run monitor polls every second and updates its widgets in place.</desc>
<rect width="{W}" height="{FLOW_H}" rx="16" fill="{t["canvas"]}"/>
<g font-family="{SANS}">{"".join(parts)}</g>
</svg>
'''


def _box(t: dict[str, str], x: float, step: Step) -> str:
    out = [f'<rect x="{x}" y="{BOX_Y}" width="{BOX_W}" height="{BOX_H}" rx="{R}" fill="{t["surface"]}" stroke="{t["border-strong"]}"/>',
           f'<text x="{x + 16}" y="{BOX_Y + 40}" font-size="24" font-weight="650" fill="{t["text"]}">{step.title}</text>',
           f'<text x="{x + 16}" y="{BOX_Y + 72}" font-family="{MONO}" font-size="18" fill="{t["accent-700"]}">{step.code}</text>']
    out += [f'<text x="{x + 16}" y="{BOX_Y + 110 + i * 30}" font-size="20" fill="{t["text-secondary"]}">{s}</text>'
            for i, s in enumerate(step.lines)]
    return "".join(out)


def _arrow(t: dict[str, str], box_x: float) -> str:
    """Arrow in the gap left of the box at box_x."""
    mid = BOX_Y + BOX_H / 2
    return (f'<path d="M{box_x - FLOW_GAP + 4} {mid} h{FLOW_GAP - 14}" stroke="{t["accent-600"]}" stroke-width="3"/>'
            f'<path d="M{box_x - 3} {mid} l-12 -9 v18 z" fill="{t["accent-600"]}"/>')


if __name__ == "__main__":
    (OUT / "hero.svg").write_text(hero(), encoding="utf-8")
    for theme_name in ("light", "dark"):
        (OUT / f"flow-{theme_name}.svg").write_text(flow(theme_name), encoding="utf-8")
    print("ok")
