from nicegui import ui
from nicegui.events import ValueChangeEventArguments

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
        ui.notify(f"Zone #{selected.id()} queued for {timer_duration} {"minutes" if timer_mode == 1 else "seconds"}")

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

def update():
    for select, zone in zip(ui_zone_selection, range(1,5)):
        if select.value:
            select_zone(zone)
        else:
            deselect_zone(zone)
    
    global zone_ctl
    zone_ctl.update()
    jobs_label.text = f"{zone_ctl.count_tasks()} jobs in queue"

ui.timer(1.0, update)
ui.run()
