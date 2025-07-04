from nicegui import ui
from nicegui.events import ValueChangeEventArguments

# int for the total amount of seconds the program has been running for
total_seconds: int = 0

class TimedTask:
    def __init__(self, delay: int, callback):
        self.executed = False
        self.start_time = total_seconds
        self.delay = delay
        self.callback = callback
    
    def get_start_time(self) -> int:
        return self.start_time
    
    def get_delay(self) -> int:
        return self.delay

    def get_end_time(self) -> int:
        return self.start_time + self.delay

    def execute(self):
        self.executed = True
        return self.callback()
    
    def was_executed(self):
        return self.executed

tasks: list[TimedTask] = []

def send_serial(message):
    print(message)

def start_zone(zone: int):
    ui.notify(f"Starting zone #{zone}")
    send_serial(f"B{zone}")
    ui.notify(f"Zone #{zone} started!")

def stop_zone(zone: int):
    ui.notify(f"Stopping zone #{zone}")
    send_serial(f"E{zone}")
    ui.notify(f"Zone #{zone} stopped!")

def schedule_stop_zone(zone: int, delay_value: float, delay_type: int):
    tasks.append(TimedTask(delay_value * (60 if delay_type == 1 else 1), lambda: stop_zone(zone)))
    ui.notify(f"Zone #{zone} will shut off in {delay_value} {"minutes" if delay_type == 1 else "seconds"}")

def stop_all_zones():
    global tasks
    for zone in range(1, 5):
        stop_zone(zone)
    tasks.clear()

zone_selection: list = []
ui.label("Selected zones")
with ui.row() as r:
    for zone in range(1, 5):
        zone_selection.append(ui.checkbox(f"{zone}", value=True))

timer_duration: float = 0
timer_mode: int = 0

def start_selected_zones():
    for selection, zone in zip(zone_selection, range(1, 5)):
        if selection.value:
            start_zone(zone)
            schedule_stop_zone(zone, timer_duration, timer_mode)
def stop_selected_zones():
    for selection, zone in zip(zone_selection, range(1, 5)):
        if selection.value:
            stop_zone(zone)

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
    ui.button(f"Stop zone(s)", on_click=stop_all_zones)

def update():
    global total_seconds
    global tasks
    total_seconds += 1

    for task in tasks:
        if task.get_end_time() <= total_seconds:
            task.execute()
    
    tasks = [task for task in tasks if not task.was_executed()]

ui.timer(1.0, update)
ui.run()
