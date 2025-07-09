from nicegui import ui
from nicegui.events import ValueChangeEventArguments

import spkrctl
from zonectl import ZoneCtl, Zone
from prog import Program, ProgramCtl
import json
from datetime import datetime

# Zone controller
zone_ctl = ZoneCtl()

# Program controller
prog_ctl = ProgramCtl()

ui.label("Configuration")
NOT_CONNECTED_STATUS = "NOT CONNECTED TO CONTROLLER"
YES_CONNECTED_STATUS = "READY TO ROCK!"
connected_status = ui.label(NOT_CONNECTED_STATUS)
time_label = ui.label(f"{datetime.now()}")

def stop_all():
    zone_ctl.clear()
    ui.notify("All zones stopped")

ui.label("Control")
with ui.row() as r:
    ui.button(f"Stop all", on_click=stop_all)

async def edit_program(program):
    if program is None:
        return
    result = await modify_prog_ui(program)
    prog_ctl.reload()
    if result == "DEL":
        prog_ctl.remove(program)
        ui.notify("Deleted!")
        return
    ui.notify("Saved")

# Program management section
ui.label("Programs:")
from prog_ui import modify_prog_ui
async def update_fucking_selection():
    global prog_ctl
    prog_ctl.reload()
    prog_select.set_options([prog.name for prog in prog_ctl.programs])
async def progs_update_bullshit():
    await modify_prog_ui(None)
    await update_fucking_selection()
async def fucking_edit_selected():
    return await edit_program(prog_ctl.get(prog_select.value))
async def fucking_delete_selected():
    prog_ctl.remove(prog_ctl.get(prog_select.value))
    await update_fucking_selection()
async def start_test_run():
    prog = prog_ctl.get(prog_select.value)
    for task in prog.tasks:
        zone_ctl.queue(zone_ctl.get(task['zone']), task['duration'])
            
prog_select = None
with ui.row():
    prog_select = ui.select([prog.name for prog in prog_ctl.programs])
    ui.button("🧪 Test Run", on_click=start_test_run)
with ui.row():
    ui.button("➕ Add", on_click=progs_update_bullshit)
    ui.button("📝 Edit", on_click=fucking_edit_selected)
    ui.button("🗑️ Delete", on_click=fucking_delete_selected)

jobs_label = ui.label("Jobs")
jobs_queue = ui.table(columns=[
    {'name':'zone', 'label':'Zone', 'field':'zone', 'required':True, 'align':'left'},
    {'name':'remaining', 'label':'Time remaining (seconds)', 'field':'remaining', 'required':True}
], rows=[])

prog_started_delay = 0
def update():
    global connected_status
    global zone_ctl
    global prog_started_delay

    if spkrctl.spkr_connected:
        connected_status.set_text(YES_CONNECTED_STATUS)
    else:
        connected_status.set_text(NOT_CONNECTED_STATUS)

    now = datetime.now()
    time_label.set_text(f"{now}")

    for prog in prog_ctl.programs:
        if prog.start_time == f"{now.hour:02d}:{now.minute}" and prog_started_delay <= 0:
            # Queue the program's tasks
            for task in prog.tasks:
                zone_ctl.queue(zone_ctl.get(task['zone']), task['duration'])
            prog_started_delay = 60 * 4
    prog_started_delay -= 1

    jobs_label.text = f"{zone_ctl.count_tasks()} jobs in queue"
    jobs_queue.update_rows([ {'zone':task.get_zone().id(), 'remaining':task.get_time_remaining()} for task in zone_ctl.get_tasks()])
    zone_ctl.update()

spkrctl.start_spkr()
ui.timer(0.25, update)
ui.run()
spkrctl.running_spkr = False