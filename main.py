from nicegui import ui
from nicegui.events import ValueChangeEventArguments

ui.label("Selected zones")
with ui.row() as r:
    for zone in range(1, 5):
        ui.checkbox(f"{zone}", value=True)

ui.label("Timer")
with ui.row() as r:
    ui.number(label="Duration")
    ui.select(["Seconds", "Minutes", "Hours"])
    ui.button("Start", on_click=lambda: ui.notify("Starting sprinklers..."))

ui.label("Control")
with ui.row() as r:
    ui.button(f"Stop zone(s)", on_click=lambda: ui.notify("All zones stopped"))

ui.run()
