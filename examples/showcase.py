"""Showcase of every kit piece.

    uv run python examples/showcase.py

-> http://127.0.0.1:8787 (?dark=1 forces dark). `/` is a sample working screen (start a
run, watch the list); `/kit` is the component gallery.
"""

from datetime import datetime, timedelta

from nicegui import ui

from nicegui_kit import layout, run_monitor, run_pool, table, theme

PERIODS = {"День": timedelta(days=1), "Неделя": timedelta(days=7), "Всё": None}
STATUSES = {"Все статусы": None, "Идёт": run_pool.PENDING_STATUSES, "Готово": {run_pool.DONE},
            "Ошибка": {run_pool.FAILED}}
DEMO_RUNS = (("Ночной сбор", "echo collecting; sleep 2; echo done"),
             ("Пробный прогон", "echo start; echo boom >&2; exit 3"))

theme.apply_theme()


def _submit(label: str, script: str) -> None:
    run_pool.submit(["sh", "-c", script], label=label)


def _run_dialog() -> ui.dialog:
    """Starting a run is a one-off act; the list is where the work is. So the form
    lives in a dialog behind the page's primary button, not in a column of its own."""
    with ui.dialog() as dialog, layout.section_card():
        layout.heading("Новый прогон", level=2)
        name = layout.field("Название", required=True, enter="next").props("clearable")
        # a filled address IS the request for a report: no separate checkbox
        mail = layout.field("Почта для отчёта (необязательно)", kind="email", enter="done",
                            hint="Пришлём отчёт, когда прогон закончится").props("clearable")

        def start() -> None:
            if not name.validate():
                return
            _submit(name.value, "echo working; sleep 3; echo ok")
            ui.notify(f"Прогон «{name.value}» запущен"
                      + (f", отчёт придёт на {mail.value}" if mail.value else ""), type="positive")
            name.value = ""
            dialog.close()

        mail.on("keydown.enter", start)
        with layout.actions_row():
            layout.button("Отмена", kind="quiet", on_click=dialog.close)
            layout.button("Запустить", kind="primary", on_click=start)
    return dialog


def _runs_section() -> None:
    flt = {"text": "", "status": "Все статусы", "period": "Всё"}

    def visible(state: run_pool.RunState) -> bool:
        statuses, age = STATUSES[flt["status"]], PERIODS[flt["period"]]
        return ((not flt["text"] or flt["text"].lower() in state.label.lower())
                and (statuses is None or state.status in statuses)
                and (age is None or datetime.now(state.created_at.tzinfo) - state.created_at <= age))

    # the page h1 already names the list; the count depends on the filters, so it sits with them
    with layout.filter_bar():
        layout.search_field("Поиск по названию", on_change=lambda e: flt.update(text=e.value or ""))
        ui.select(list(STATUSES), value="Все статусы",
                  on_change=lambda e: flt.update(status=e.value)) \
            .props('outlined dense aria-label="Статус"')
        ui.toggle(list(PERIODS), value="Всё", on_change=lambda e: flt.update(period=e.value))
        ui.space()
        count = ui.label().classes("t-meta")
    run_monitor.attach_run_monitor(run_filter=visible, idle_text="Под эти фильтры прогонов нет.")
    ui.timer(1, lambda: count.set_text(
        f"Показано {sum(map(visible, run_pool.RUNS.values()))} из {len(run_pool.RUNS)}"))


def _states_gallery() -> None:
    with layout.section_card():
        layout.heading("Состояния данных", level=2)
        ui.label("Одно место — одно состояние; переключите, чтобы сравнить.").classes("t-meta")
        area = ui.column().classes("w-full")

        def show(kind: str) -> None:
            area.clear()
            with area:
                if kind == "Пусто":
                    layout.empty("Прогонов ещё не было — запустите первый.",
                                 ("Запустить", lambda: ui.notify("Демо")))
                elif kind == "Загрузка":
                    layout.waiting("Загружаем журнал")
                elif kind == "Ошибка":
                    layout.failed("Не удалось прочитать журнал. Проверьте путь в настройках.",
                                  retry=lambda: ui.notify("Повтор"))
                else:
                    with ui.row().classes("ic-state"):
                        ui.icon("check_circle").classes("ic-status--ok")
                        ui.label("Журнал прочитан: 1 204 записи.").classes("ic-status--ok")

        ui.toggle(["Пусто", "Загрузка", "Ошибка", "Готово"], value="Пусто",
                  on_change=lambda e: show(e.value))
        show("Пусто")


def _fields_gallery() -> None:
    with layout.section_card():
        layout.heading("Поля ввода", level=2)
        ui.label("Тип поля задаёт клавиатуру на телефоне и автозаполнение браузера.").classes("t-meta")
        with layout.grid():
            layout.field("Город", suggestions=["Москва", "Минск", "Мурманск"],
                         hint="Подсказки при вводе").classes("ic-span-6")
            layout.field("Телефон", kind="tel", hint="Цифровая клавиатура").classes("ic-span-6")
            layout.field("Пароль", kind="password", required=True).classes("ic-span-6")
            layout.field("Код из СМС", kind="code", enter="done", hint="6 цифр") \
                .props('mask="### ###" unmasked-value input-class="t-mono"').classes("ic-span-4")


def _marks_gallery() -> None:
    with layout.section_card():
        layout.heading("Статусы и метки", level=2)
        with ui.row().classes("items-center flex-wrap").style("gap: var(--ic-s2) var(--ic-s3)"):
            for text, cls in (("готово", "ok"), ("идёт", "running"), ("ошибка", "error"),
                              ("остановлено", "cancel")):
                ui.label(text).classes(f"ic-badge ic-status--{cls}")
            ui.label("12").classes("ic-count")
            ui.label("prod").classes("ic-chip ic-chip--neutral")
        ui.label("Токен истекает через 2 дня — обновите его в настройках.").classes("ic-banner p-3")


def _data_gallery() -> None:
    with layout.section_card():
        layout.heading("Таблица и текст", level=2)
        t = table.empty_aware_table(
            [{"name": "n", "label": "Автор", "field": "n", "align": "left"},
             {"name": "c", "label": "Видео", "field": "c", "align": "right"}],
            row_key="n", pagination={"rowsPerPage": 0},
        )
        t.table.props("hide-bottom")
        t.set_rows([{"n": "alice", "c": 1204}, {"n": "борис", "c": 37}])
        layout.markdown_reader("## Сводка\n\nТекст с `кодом` и [ссылкой](#).\n\n> цитата")


PAGES = {"/": "Пример экрана", "/kit": "Компоненты"}
# every page says it is a sample: nobody should mistake it for a working tool
DEMO_NOTE = "Это демо-шаблон nicegui-kit: пример, чтобы посмотреть GUI в работе. Данные ненастоящие."


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
            layout.heading("Пример: прогоны задач", level=1)
            layout.button("Новый прогон", kind="primary", icon="add", on_click=dialog.open)
        with ui.column().classes("w-full").style("gap: var(--ic-s4)"):
            _runs_section()


@ui.page("/kit")
def kit(dark: int = 0) -> None:
    _shell("/kit", dark, layout.PAGE_MAX_WIDTH_WIDE)
    with layout.page_container(max_width=layout.PAGE_MAX_WIDTH_WIDE):
        layout.heading("Компоненты kit", level=1)
        ui.label("Витрина для разработчика: каждый блок — один компонент во всех его состояниях.") \
            .classes("t-meta")
        with layout.grid():
            # pairs of similar height; a card fills its grid row, so no ragged holes
            for part in (_states_gallery, _marks_gallery, _fields_gallery, _data_gallery):
                with ui.column().classes("ic-span-6 w-full"):
                    part()


ui.run(host="127.0.0.1", port=8787, show=False, reload=False, language="ru",
       title="nicegui-kit · демо-шаблон")
