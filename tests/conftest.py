"""nicegui's `user` test fixture isn't auto-registered via entry_points in this
version, so wire it in explicitly for the one test that needs a real page."""

pytest_plugins = ["nicegui.testing.user_plugin"]
