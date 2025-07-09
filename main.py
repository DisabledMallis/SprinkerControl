from nicegui import ui
from nicegui.events import ValueChangeEventArguments

import spkrctl
from zonectl import ZoneCtl, Zone
from prog import Program, ProgramCtl
import json

# Zone controller
zone_ctl = ZoneCtl()

# Program controller
prog_ctl = ProgramCtl()

ui.label("Configuration")
NOT_CONNECTED_STATUS = "NOT CONNECTED TO CONTROLLER"
YES_CONNECTED_STATUS = "READY TO ROCK!"
connected_status = ui.label(NOT_CONNECTED_STATUS)

def stop_all():
    zone_ctl.clear()
    ui.notify("All zones stopped")

ui.label("Control")
with ui.row() as r:
    ui.button(f"Stop all", on_click=stop_all)

def run_program(program):
    ui.notify(f"Running '{program.name}'")
ui.label("Programs:")
with ui.list().props('bordered separator'):
    ui.item_label('Programs').props('header').classes('text-bold')
    ui.separator()
    for program in prog_ctl.programs:
        with ui.item(on_click=lambda: run_program(program)):
            with ui.item_section().props('avatar'):
                ui.icon('settings')
            with ui.item_section():
                ui.item_label(program.name)
                ui.item_label(program.start_time).props('caption')
            with ui.item_section().props('avatar'):
                ui.icon('start')


with ui.dialog() as prog_dialog, ui.card():
    prog = Program()
    editor = ui.codemirror(value=prog.to_json(), language='JSON')

    with ui.row():
        ui.button("Save", on_click=lambda: prog_dialog.submit(prog))
        ui.button("Cancel", on_click=lambda: prog_dialog.submit(None))

async def show_prog_dialog():
    prog = await prog_dialog
    if prog is not None:
        ui.notify(f"Saved '{prog.name}'")
        prog_ctl.save(prog)
    else:
        ui.notify("Aborted")

jobs_label = ui.label("Jobs")
jobs_queue = ui.table(columns=[
    {'name':'zone', 'label':'Zone', 'field':'zone', 'required':True, 'align':'left'},
    {'name':'remaining', 'label':'Time remaining (seconds)', 'field':'remaining', 'required':True}
], rows=[])

def update():
    global connected_status
    global zone_ctl

    if spkrctl.spkr_connected:
        connected_status.set_text(YES_CONNECTED_STATUS)
    else:
        connected_status.set_text(NOT_CONNECTED_STATUS)

    jobs_label.text = f"{zone_ctl.count_tasks()} jobs in queue"
    jobs_queue.update_rows([ {'zone':task.get_zone().id(), 'remaining':task.get_time_remaining()} for task in zone_ctl.get_tasks()])
    zone_ctl.update()

spkrctl.start_spkr()
ui.timer(0.25, update)
ui.run()
spkrctl.running_spkr = False