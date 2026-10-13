"""The showcase is the kit's visual reference: it must render and its flows must work."""

import asyncio
from pathlib import Path

import pytest
from nicegui import ui
from nicegui.testing import User

DEMO_NOTE = "Это демо-шаблон nicegui-kit"
MAIN = str(Path(__file__).parents[1] / "examples" / "showcase.py")


@pytest.mark.nicegui_main_file(MAIN)
async def test_runs_show_and_dialog_starts_a_run(user: User) -> None:
    await user.open("/")
    await asyncio.sleep(4)
    await user.should_see(DEMO_NOTE)
    await user.should_see("Пробный прогон")
    await user.should_see("ошибка · код 3")
    user.find("Новый прогон").click()
    name = next(i for i in user.current_layout.descendants()
                if isinstance(i, ui.input) and i.props.get("label") == "Название")
    name.value = "проверка"
    user.find("Запустить").click()
    await user.should_see("Прогон «проверка» запущен")


@pytest.mark.nicegui_main_file(MAIN)
async def test_kit_page(user: User) -> None:
    await user.open("/kit")
    await user.should_see(DEMO_NOTE)
    await user.should_see("Состояния данных")
    await user.should_not_see("Новый прогон")
