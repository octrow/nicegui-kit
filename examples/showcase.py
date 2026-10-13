"""Showcase of every kit piece.

    uv run python examples/showcase.py

-> http://127.0.0.1:8787 (?dark=1 forces dark). `/` is a sample working screen (start a
run, watch the list); `/kit` is the component gallery.
"""

import sys
from datetime import datetime, timedelta

from nicegui import ui

from nicegui_kit import layout, run_monitor, run_pool, table, texts, theme

PERIODS = {"Day": timedelta(days=1), "Week": timedelta(days=7), "All": None}
STATUSES = {"All statuses": None, "Running": run_pool.PENDING_STATUSES, "Done": {run_pool.DONE},
            "Error": {run_pool.FAILED}}
DEMO_RUNS = (("Nightly scrape", "import time; print('collecting', flush=True); time.sleep(2); print('done')"),
             ("Trial run", "import sys; print('start', flush=True); print('boom', file=sys.stderr); sys.exit(3)"))

texts.TEXTS.update(texts.EN)  # kit strings are Russian by default
theme.apply_theme()


def _submit(label: str, script: str) -> None:
    run_pool.submit([sys.executable, "-c", script], label=label)  # no shell: runs on Windows too


def _run_dialog() -> ui.dialog:
    """Starting a run is a one-off act; the list is where the work is. So the form
    lives in a dialog behind the page's primary button, not in a column of its own."""
    with ui.dialog() as dialog, layout.section_card():
        layout.heading("New run", level=2)
        name = layout.field("Name", required=True, enter="next").props("clearable")
        # a filled address IS the request for a report: no separate checkbox
        mail = layout.field("Email for the report (optional)", kind="email", enter="done",
                            hint="We'll send a report when the run finishes").props("clearable")

        def start() -> None:
            if not name.validate():
                return
            _submit(name.value, "import time; print('working', flush=True); time.sleep(3); print('ok')")
            ui.notify(f"Run \"{name.value}\" started"
                      + (f", the report will go to {mail.value}" if mail.value else ""), type="positive")
            name.value = ""
            dialog.close()

        mail.on("keydown.enter", start)
        with layout.actions_row():
            layout.button("Cancel", kind="quiet", on_click=dialog.close)
            layout.button("Start", kind="primary", on_click=start)
    return dialog


def _runs_section() -> None:
    flt = {"text": "", "status": "All statuses", "period": "All"}

    def visible(state: run_pool.RunState) -> bool:
        statuses, age = STATUSES[flt["status"]], PERIODS[flt["period"]]
        return ((not flt["text"] or flt["text"].lower() in state.label.lower())
                and (statuses is None or state.status in statuses)
                and (age is None or datetime.now(state.created_at.tzinfo) - state.created_at <= age))

    # the page h1 already names the list; the count depends on the filters, so it sits with them
    with layout.filter_bar():
        layout.search_field("Search by name", on_change=lambda e: flt.update(text=e.value or ""))
        ui.select(list(STATUSES), value="All statuses",
                  on_change=lambda e: flt.update(status=e.value)) \
            .props('outlined dense aria-label="Status"')
        ui.toggle(list(PERIODS), value="All", on_change=lambda e: flt.update(period=e.value))
        ui.space()
        count = ui.label().classes("t-meta")
    run_monitor.attach_run_monitor(run_filter=visible, idle_text="No runs match these filters.")
    ui.timer(1, lambda: count.set_text(
        f"Showing {sum(map(visible, run_pool.RUNS.values()))} of {len(run_pool.RUNS)}"))


def _states_gallery() -> None:
    with layout.section_card():
        layout.heading("Data states", level=2)
        ui.label("One place, one state at a time; switch to compare.").classes("t-meta")
        area = ui.column().classes("w-full")

        def show(kind: str) -> None:
            area.clear()
            with area:
                if kind == "Empty":
                    layout.empty("No runs yet. Start the first one.",
                                 ("Start", lambda: ui.notify("Demo")))
                elif kind == "Loading":
                    layout.waiting("Loading the journal")
                elif kind == "Error":
                    layout.failed("Couldn't read the journal. Check the path in settings.",
                                  retry=lambda: ui.notify("Retry"))
                else:
                    with ui.row().classes("ic-state"):
                        ui.icon("check_circle").classes("ic-status--ok")
                        ui.label("Journal read: 1,204 entries.").classes("ic-status--ok")

        ui.toggle(["Empty", "Loading", "Error", "Done"], value="Empty",
                  on_change=lambda e: show(e.value))
        show("Empty")


def _fields_gallery() -> None:
    with layout.section_card():
        layout.heading("Input fields", level=2)
        ui.label("The field kind sets the phone keyboard and browser autofill.").classes("t-meta")
        with layout.grid():
            layout.field("City", suggestions=["Berlin", "Boston", "Bristol"],
                         hint="Suggestions while typing").classes("ic-span-6")
            layout.field("Phone", kind="tel", hint="Numeric keypad").classes("ic-span-6")
            layout.field("Password", kind="password", required=True).classes("ic-span-6")
            layout.field("SMS code", kind="code", enter="done", hint="6 digits") \
                .props('mask="### ###" unmasked-value input-class="t-mono"').classes("ic-span-4")


def _marks_gallery() -> None:
    with layout.section_card():
        layout.heading("Statuses and marks", level=2)
        with ui.row().classes("items-center flex-wrap").style("gap: var(--ic-s2) var(--ic-s3)"):
            for text, cls in (("done", "ok"), ("running", "running"), ("error", "error"),
                              ("cancelled", "cancel")):
                ui.label(text).classes(f"ic-badge ic-status--{cls}")
            ui.label("12").classes("ic-count")
            ui.label("prod").classes("ic-chip ic-chip--neutral")
        ui.label("The token expires in 2 days. Renew it in settings.").classes("ic-banner p-3")


def _data_gallery() -> None:
    with layout.section_card():
        layout.heading("Table and text", level=2)
        t = table.empty_aware_table(
            [{"name": "n", "label": "Author", "field": "n", "align": "left"},
             {"name": "c", "label": "Videos", "field": "c", "align": "right"}],
            row_key="n", pagination={"rowsPerPage": 0},
        )
        t.table.props("hide-bottom")
        t.set_rows([{"n": "alice", "c": 1204}, {"n": "bob", "c": 37}])
        layout.markdown_reader("## Summary\n\nText with `code` and a [link](#).\n\n> a quote")


PAGES = {"/": "Sample screen", "/kit": "Components"}
# every page says it is a sample: nobody should mistake it for a working tool
DEMO_NOTE = "This is a nicegui-kit demo: a sample to see the GUI at work. The data is not real."


def _shell(here: str, dark: int, max_width: str) -> None:
    if dark:
        ui.dark_mode(True)
    # the header row has the page's width and side padding: brand and toggle line up with content
    header = ui.header().style("flex-direction: column; align-items: stretch;"
                               " gap: var(--ic-s3); padding: var(--ic-s3) 0 0")
    with header, ui.row().classes(f"ic-split w-full {max_width} mx-auto items-center justify-between") \
            .style("padding: 0 var(--ic-s6); flex-wrap: nowrap"):
        with ui.row().classes("items-center").style("gap: var(--ic-s4) var(--ic-s6); flex-wrap: nowrap; min-width: 0"):
            ui.label("nicegui-kit").classes("t-brand gt-xs")  # phones: the nav names the page
            with ui.element("nav").style("display: flex; flex-direction: row; gap: var(--ic-s4)"):
                for path, title in PAGES.items():
                    link = ui.link(title, path + (f"?dark={dark}" if dark else "")).classes("ic-nav-link")
                    if path == here:
                        link.classes("ic-nav-link--here").props('aria-current="page"')
        theme.theme_toggle()
    with header:
        ui.label(DEMO_NOTE).classes("t-meta w-full").props('role="note"').style(
            "background: var(--ic-accent-100); color: var(--ic-text); text-align: center;"
            " padding: var(--ic-s1) var(--ic-s4)")


@ui.page("/")
def index(dark: int = 0) -> None:
    if not run_pool.RUNS:
        for label, script in DEMO_RUNS:
            _submit(label, script)
    # a list reads best at a line length the eye can sweep: name ... status time
    _shell("/", dark, layout.PAGE_MAX_WIDTH_FORM)
    dialog = _run_dialog()
    with layout.page_container():
        with ui.row().classes("ic-split w-full items-center justify-between"):
            layout.heading("Sample: job runs", level=1)
            layout.button("New run", kind="primary", icon="add", on_click=dialog.open)
        with ui.column().classes("w-full").style("gap: var(--ic-s4)"):
            _runs_section()


@ui.page("/kit")
def kit(dark: int = 0) -> None:
    _shell("/kit", dark, layout.PAGE_MAX_WIDTH_WIDE)
    with layout.page_container(max_width=layout.PAGE_MAX_WIDTH_WIDE):
        layout.heading("Kit components", level=1)
        ui.label("A gallery for developers: each card is one component in all its states.") \
            .classes("t-meta")
        with layout.grid():
            # pairs of similar height; a card fills its grid row, so no ragged holes
            for part in (_states_gallery, _marks_gallery, _fields_gallery, _data_gallery):
                with ui.column().classes("ic-span-6 w-full"):
                    part()


ui.run(host="127.0.0.1", port=8787, show=False, reload=False, language="en-US",
       title="nicegui-kit · demo")
