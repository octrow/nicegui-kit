"""The showcase is the kit's visual reference: it must render and its flows must work."""

import asyncio
from pathlib import Path

import pytest
from nicegui import ui
from nicegui.testing import User

from nicegui_kit import texts

DEMO_NOTE = "This is a nicegui-kit demo"
MAIN = str(Path(__file__).parents[1] / "examples" / "showcase.py")


@pytest.fixture(autouse=True)
def _restore_russian():
    """The showcase switches the process-global kit strings to English."""
    yield
    texts.TEXTS.update(texts.RU)


@pytest.mark.nicegui_main_file(MAIN)
async def test_runs_show_and_dialog_starts_a_run(user: User) -> None:
    await user.open("/")
    await asyncio.sleep(4)
    await user.should_see(DEMO_NOTE)
    await user.should_see("Trial run")
    await user.should_see("error · code 3")
    user.find("New run").click()
    name = next(i for i in user.current_layout.descendants()
                if isinstance(i, ui.input) and i.props.get("label") == "Name")
    name.value = "check"
    user.find("Start").click()
    await user.should_see('Run "check" started')


@pytest.mark.nicegui_main_file(MAIN)
async def test_kit_page(user: User) -> None:
    await user.open("/kit")
    await user.should_see(DEMO_NOTE)
    await user.should_see("Data states")
    await user.should_not_see("New run")
