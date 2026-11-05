# План: nicegui-kit

Открытые баги, планы и идеи репозитория. Дата: 2026-11-05. Закрытый пункт удаляется или получает ✅ со ссылкой на коммит.

Номера #N: [docs/plans/2026-11-05-logic-map-fixes.md](docs/plans/2026-11-05-logic-map-fixes.md). Открытых GitHub issues нет.

## Баги

MEDIUM (все в `run_pool.py`):
- [x] ✅ 2026-11-05 #1: `submit` убирает запуск из `RUNS` и пробрасывает исключение, если `spawn` упал; не закоммичено. (было: при ошибке `spawn` запуск остаётся `queued` в `RUNS` и занимает лимит 20; убрать из `RUNS` или пометить `failed` ([план](docs/plans/2026-11-05-logic-map-fixes.md), `run_pool.py:135`))
- [x] #2: ✅ 2026-11-05 — `env={}` и `env=None` одинаково наследуют окружение, непустой `env` заменяет его без merge; решить и описать (вопрос владельцу)
- [x] #3: ✅ 2026-11-05 — только `terminate()`, ребёнок, игнорирующий SIGTERM, держит слот; 3 таких замораживают пул; нужен `kill()` после таймаута (вопрос владельцу; [system-design](docs/system-design.md#risks))
- [x] #9: ✅ 2026-11-05 — внук держит stdout, запуск вечно `running`, Stop не работает; `start_new_session` и `killpg` вместе с #3 ([system-design](docs/system-design.md#risks))
- [ ] `RunState.lines` без лимита: 149 МБ на 1M строк, до ~3.4 ГБ на 23 сохранённых запуска ([system-design](docs/system-design.md#risks), `run_pool.py:155`)

LOW (по списку, детали в плане):
- [ ] #8 (частично ✅ 2026-11-05: неожиданное исключение в `_execute` теперь `failed` со строкой в логе, пустой argv уже давал `failed`; не закоммичено): любое неожиданное исключение в `_execute` превращается в `cancelled`; `submit([])` падает с IndexError; нужен `failed` и отказ на пустой argv
- [ ] #7 ✅ 2026-11-05 (`storage_key` через `json.dumps` в `table.py`, не закоммичено); #4, #5, #6, #10, #11, #12, #13: мелкие дефекты `run_monitor.py`, `table.py`, `theme.py` ([таблица](docs/plans/2026-11-05-logic-map-fixes.md#findings))

## Планы и фичи

- [ ] Порядок правок из плана: 1) #1, #2, #3, #9, #8 в `run_pool.py` с тестами в `tests/test_run_pool.py`; 2) #4, #5, #10, #11, #13 в `run_monitor.py`; 3) #6, #7, #12 в `table.py` / `theme.py` ([план](docs/plans/2026-11-05-logic-map-fixes.md#order-of-work))
- [ ] Каждая находка плана получает ✅ или решение "оставить как есть" с причиной ([план](docs/plans/2026-11-05-logic-map-fixes.md#done-when))
- [ ] В "Known gaps" в `docs/logic-map.md` перечислены все открытые HIGH и MEDIUM находки ([план](docs/plans/2026-11-05-logic-map-fixes.md#done-when))
- [ ] Следующая ступень: лимит на `lines` (кольцевой буфер или сброс в файл) и пакетная отправка строк за тик; триггер: RSS хоста > 500 МБ или тик > 250 мс ([system-design, раздел 8](docs/system-design.md#8-summary))

## Идеи

- [ ] Таймаут запуска (общий лимит времени на run) ([system-design](docs/system-design.md#6-scale-and-failure))
- [ ] Персистентность: лог каждого запуска в файл, если запуски должны переживать рестарт хоста ([system-design](docs/system-design.md#5-data))
- [ ] Настоящая очередь задач с отдельным воркером, только если нужна устойчивость к рестарту ([system-design](docs/system-design.md#8-summary))
- [ ] Тик монитора 1 Гц: первое узкое место при x10 вкладок или строк; пакетный push ([system-design](docs/system-design.md#risks), `run_monitor.py:176`)
- [ ] Лимиты ресурсов дочерних процессов (сейчас вне рамок) ([system-design](docs/system-design.md#1-requirements))

## Подробные планы

- [docs/plans/2026-11-05-logic-map-fixes.md](docs/plans/2026-11-05-logic-map-fixes.md): находки карты логики, порядок работ
- [docs/logic-map.md](docs/logic-map.md): как команда становится запуском, все ветки
- [docs/system-design.md](docs/system-design.md): расчёт нагрузки, отказы, риски (2026-11-05)
- Сводка по всем репо: `~/dev/docs/system-design-report-2026-11-05.md`
- [DESIGN.md](DESIGN.md), [docs/api.md](docs/api.md): правила дизайна и публичный API
- [docs/skills-roadmap-2026-11-05.md](docs/skills-roadmap-2026-11-05.md): навыки с рынка вакансий, 1 пункт: Dockerfile + compose для examples/ и образ в release.yml
