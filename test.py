from nicegui import ui

ui.label("Michael Gorney")
ui.button("Click Me!", on_click=lambda x: ui.notify("I was clicked"))
ui.run()