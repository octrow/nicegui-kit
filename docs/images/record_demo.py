"""Re-record docs/images/demo.gif from examples/showcase.py (about 16 s: new run, live log, search, dark theme).

    uv run python examples/showcase.py &   # serves :8787 on fresh state
    uv run --no-project --with playwright python docs/images/record_demo.py /tmp/demo-video
    F="trim=start=0.6,setpts=PTS-STARTPTS,fps=12,scale=960:-1:flags=lanczos"
    ffmpeg -i /tmp/demo-video/*.webm -vf "${F},palettegen=max_colors=128:stats_mode=diff" /tmp/pal.png
    ffmpeg -i /tmp/demo-video/*.webm -i /tmp/pal.png -lavfi "${F}[x];[x][1:v]paletteuse=dither=bayer:bayer_scale=4:diff_mode=rectangle" docs/images/demo.gif
"""
import os
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8787"
W, H = 1100, 640
out = Path(sys.argv[1])

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=os.environ.get("CHROME"))  # unset: playwright's own chromium
    ctx = browser.new_context(viewport={"width": W, "height": H}, color_scheme="light",
                              record_video_dir=str(out), record_video_size={"width": W, "height": H})
    page = ctx.new_page()
    page.goto(BASE + "/")
    page.wait_for_selector(".ic-run")
    page.wait_for_timeout(1800)

    page.get_by_role("button", name="New run").click()
    page.wait_for_timeout(600)
    page.get_by_label("Name", exact=True).press_sequentially("Weekly report", delay=70)
    page.wait_for_timeout(400)
    page.get_by_role("button", name="Start").click()
    page.wait_for_timeout(700)

    # the monitor opens a fresh run's log by itself (run_monitor.py); a click here would close it again
    page.locator(".ic-run.q-expansion-item--expanded", has_text="Weekly report").wait_for()
    page.wait_for_timeout(4200)  # working ... ok

    search = page.get_by_label("Search by name")
    search.press_sequentially("trial", delay=90)
    page.wait_for_timeout(1500)
    search.fill("")
    page.wait_for_timeout(900)

    toggle = page.locator(".ic-btn-ctl").first
    for _ in range(3):  # cycle the theme until the page is dark
        if page.evaluate("document.body.classList.contains('body--dark')"):
            break
        toggle.click()
        page.wait_for_timeout(700)
    page.mouse.move(W - 5, H - 5)
    page.wait_for_timeout(2200)
    ctx.close()
    browser.close()
