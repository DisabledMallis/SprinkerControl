from nicegui import ui
from nicegui.events import ValueChangeEventArguments

from spkrctl import SpkrCtl, spkr_ctl, UnexpectedBootError
from zonectl import ZoneCtl, Zone

# Zone controller
zone_ctl = ZoneCtl()
zone_select: list[Zone] = [None for i in range(1,5)]
def select_zone(zone: int):
    global zone_ctl
    global zone_select
    if not zone_ctl.has(zone):
        ui.notify(f"Cannot select zone: Zone #{zone} doesn't exist!")
        return

    zone_select[zone-1] = zone_ctl.get(zone)

def deselect_zone(zone: int):
    global zone_ctl
    global zone_select
    if not zone_ctl.has(zone):
        ui.notify(f"Cannot deselect zone: Zone #{zone} doesn't exist!")
        return
    
    zone_select[zone-1] = None

ui.label("Configuration")
NOT_CONNECTED_STATUS = "NOT CONNECTED TO CONTROLLER"
YES_CONNECTED_STATUS = "READY TO ROCK!"
connected_status = ui.label(NOT_CONNECTED_STATUS)

ui_zone_selection: list = []
ui.label("Selected zones")
with ui.row() as r:
    for zone in range(1, 5):
        ui_zone_selection.append(ui.checkbox(f"{zone}", value=True))

timer_duration: float = 0
timer_mode: int = 0

def start_selected_zones():
    if zone_select == None or all(v is None for v in zone_select):
        ui.notify("You must select a zone first!")
        return
    for selected in zone_select:
        if selected is None:
            continue

        ui.notify(f"Adding zone #{selected.id()} to queue")
        global zone_ctl
        duration_seconds = timer_duration * (60 if timer_mode == 1 else 1)
        zone_ctl.queue(selected, duration_seconds)
        duration_text = "minutes" if timer_mode == 1 else "seconds";
        ui.notify(f"Zone #{selected.id()} queued for {timer_duration} {duration_text}")

def stop_all():
    ui.notify(f"Stopping all zones...")
    global zone_ctl
    zone_ctl.clear()
    ui.notify(f"All zones stopped!")

def update_timer_mode(select):
    global timer_mode
    if select.value == "Minutes":
        timer_mode = 1
    elif select.value == "Seconds":
        timer_mode = 0

def update_timer_duration(num):
    global timer_duration
    timer_duration = num.value

ui.label("Timer")
with ui.row() as r:
    ui.number(label="Duration", on_change=update_timer_duration)
    ui.select(["Seconds", "Minutes"], on_change=update_timer_mode)
    ui.button("Start", on_click=start_selected_zones)

ui.label("Control")
with ui.row() as r:
    ui.button(f"Stop all", on_click=stop_all)

jobs_label = ui.label("Jobs")
jobs_queue = ui.table(columns=[
    {'name':'zone', 'label':'Zone', 'field':'zone', 'required':True, 'align':'left'},
    {'name':'remaining', 'label':'Time remaining (seconds)', 'field':'remaining', 'required':True}
], rows=[])

def update():
    global spkr_ctl
    global connected_status
    if spkr_ctl is not None:
        if not spkr_ctl.initialized() and not spkr_ctl.initialize():
            status = NOT_CONNECTED_STATUS
        else:
            status = YES_CONNECTED_STATUS
        connected_status.set_text(status)
        print(status)
        try:
            spkr_ctl.ping()
        except UnexpectedBootError as ube:
            print("[!] Unexpected reboot")
            ui.notify("Unexpected reboot, you may need to re-queue zones.")
    else:
        print("Missing spkr_ctl")
        try:
            spkr_ctl = SpkrCtl()
        except Exception as e:
            pass

    for select, zone in zip(ui_zone_selection, range(1,5)):
        if select.value:
            select_zone(zone)
        else:
            deselect_zone(zone)
    
    try:
        global zone_ctl
        zone_ctl.update()
        jobs_label.text = f"{zone_ctl.count_tasks()} jobs in queue"

        jobs_queue.update_rows([ {'zone':task.get_zone().id(), 'remaining':task.get_time_remaining()} for task in zone_ctl.get_tasks()])
    except UnexpectedBootError as ube:
        print("[!] Unexpected reboot")
        ui.notify("Unexpected reboot, you may need to re-queue zones.")


ui.timer(1.0, update)
ui.run()
