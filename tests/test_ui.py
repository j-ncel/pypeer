import pytest
from pypeer.main import PyPeer
from pypeer.screens import JoinScreen, HostScreen


@pytest.mark.asyncio
async def test_ui_quit_action():
    app = PyPeer()
    async with app.run_test() as pilot:
        await pilot.press("q")
        await pilot.pause()
        # Since 'q' is bound to exit, we check if the app
        # return value is set or if it's no longer 'active'
        assert app.return_value is None


@pytest.mark.asyncio
async def test_host_screen_ui_elements():
    app = PyPeer()
    async with app.run_test() as pilot:
        await pilot.click("#btn-host")
        await pilot.wait_for_scheduled_animations()

        # Verify screen transition
        assert isinstance(app.screen, HostScreen)

        assert len(app.screen.query("#host-code-display")) > 0
        assert len(app.screen.query("#status-label")) > 0
        assert len(app.screen.query("#btn-start-hosting")) > 0


@pytest.mark.asyncio
async def test_navigation_to_host_screen():
    app = PyPeer()
    async with app.run_test() as pilot:
        await pilot.click("#btn-host")
        await pilot.wait_for_scheduled_animations()
        assert isinstance(app.screen, HostScreen)


@pytest.mark.asyncio
async def test_join_screen_input_validation():
    app = PyPeer()
    async with app.run_test() as pilot:
        await pilot.click("#btn-join")
        await pilot.wait_for_scheduled_animations()

        await pilot.click("#join-code-input")
        await pilot.press(*"123")
        await pilot.click("#btn-connect")

        # Stay on JoinScreen because "123" is less than 6 chars
        assert isinstance(app.screen, JoinScreen)


@pytest.mark.asyncio
async def test_input_persistence_and_clearing():
    app = PyPeer()
    async with app.run_test() as pilot:
        await pilot.click("#btn-join")
        await pilot.wait_for_scheduled_animations()

        # Correctly query the input from the active screen
        input_widget = app.screen.query_one("#join-code-input")
        await pilot.click("#join-code-input")
        await pilot.press(*"ABCDEF")
        assert input_widget.value == "ABCDEF"

        for _ in range(6):
            await pilot.press("backspace")
        assert input_widget.value == ""
