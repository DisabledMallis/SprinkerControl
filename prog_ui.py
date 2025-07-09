from nicegui import ui
from prog import Program, ProgramCtl

edit_prog = Program()
edit_task = dict()
with ui.dialog() as create_task_dialog, ui.card():
    ui.label("New Task")

    duration_value = 15
    duration_minutes = False
    def set_zone(x):
        global edit_task
        edit_task['zone'] = int(x.value)
    def set_duration():
        global edit_task
        edit_task['duration'] = duration_value * (60 if duration_minutes else 1)
    def set_duration_value(x):
        global duration_value
        try:
            duration_value = int(x.value)
        except Exception as e:
            duration_value = -1
        set_duration()
    def set_duration_unit(x):
        global duration_minutes
        duration_minutes = (x.value == "Minutes")
        set_duration()

    with ui.row():
        ui.select(options=[zone for zone in range(1, 5)], label="Zone", on_change=set_zone)
        ui.input("Duration", placeholder="30", on_change=set_duration_value)
        ui.select(["Seconds", "Minutes"], on_change=set_duration_unit)

    with ui.row():
        ui.button("Done", on_click=lambda: create_task_dialog.submit(edit_task))
        ui.button("Cancel", on_click=lambda: create_task_dialog.submit(None))

async def create_task_ui():
    edit_task = await create_task_dialog
    if edit_task is None:
        return None
    if edit_task['duration'] < 0:
        ui.notify("Invalid duration value")
        return None
    return edit_task

with ui.dialog() as edit_tasks_dialog, ui.card():
    ui.label("Edit Tasks")

    task_table = ui.table(columns=[
        {'name':'zone', 'label':'Zone', 'field':'zone', 'required':True, 'align':'left'},
        {'name':'duration', 'label':'Duration (seconds)', 'field':'duration', 'required':True}
    ], rows=[])

    def clear_tasks():
        global edit_prog
        edit_prog.tasks.clear()
        task_table.update_rows(edit_prog.tasks)
    async def add_task():
        global edit_prog
        edit_task = await create_task_ui()
        if edit_task is not None:
            edit_prog.tasks.append(edit_task.copy())
        task_table.update_rows(edit_prog.tasks)

    with ui.row():
        ui.button("+ Task", on_click=add_task)
        ui.button("Clear", on_click=clear_tasks)
    with ui.row():
        ui.button("Done", on_click=lambda: edit_tasks_dialog.submit(edit_prog.tasks))
        ui.button("Cancel", on_click=lambda: edit_tasks_dialog.submit(None))
async def edit_tasks_ui():
    tasks = await edit_tasks_dialog
    if tasks is None:
        return None
    return tasks

days = ['M', 'T', 'W', 'R', 'F', 'S', 'U']

def make_create_prog_dialog():
    with ui.dialog() as create_prog_dialog, ui.card():
        title_label = ui.label("New Program")

        def set_name(x):
            global edit_prog
            edit_prog.name = x.value
        ui.input(label="Name", value=edit_prog.name, on_change=set_name)

        days_select = []
        def set_days(x):
            global edit_prog
            edit_prog.days.clear()
            for box, i in zip(days_select, range(0, len(days_select))):
                if box.value:
                    edit_prog.days.append(days[i])
        with ui.row():
            for day in days:
                check = day in edit_prog.days
                days_select.append(ui.checkbox(day, value=check, on_change=set_days))

        def set_time(x):
            global edit_prog
            edit_prog.start_time = x.value
        with ui.input('Time', value=edit_prog.start_time, on_change=set_time) as time:
            with ui.menu().props('no-parent-event') as menu:
                with ui.time().bind_value(time):
                    with ui.row().classes('justify-end'):
                        ui.button('Close', on_click=menu.close).props('flat')
            with time.add_slot('append'):
                ui.icon('access_time').on('click', menu.open).classes('cursor-pointer')

        def set_tasks(x):
            global edit_prog
            edit_prog.tasks = x.value
        with ui.row():
            tasks_label = ui.label("No tasks")
            async def open_task_edit():
                tasks = await edit_tasks_ui()
                tasks_label.set_text(f"{len(tasks)} tasks")
            ui.button("Edit Tasks", on_click=open_task_edit)

        with ui.row():
            async def run_now():
                edit_prog.run_now = True
                return create_prog_dialog.submit(edit_prog)
            async def delete_entry():
                return create_prog_dialog.submit("DEL")
            ui.button("Save", on_click=lambda: create_prog_dialog.submit(edit_prog))
            ui.button("Cancel", on_click=lambda: create_prog_dialog.submit(None))
    return create_prog_dialog
create_prog_dialog = make_create_prog_dialog()

async def modify_prog_ui(to_edit: Program = None):
    global edit_prog
    global create_prog_dialog

    if to_edit is not None:
        edit_prog = to_edit
        edit_task = dict()
        create_prog_dialog = make_create_prog_dialog()
        print(f"Editing {to_edit.name}")
    prog = await create_prog_dialog
    if prog is None:
        return None
    if prog == "DEL":
        return prog
    ui.notify("Program created!")
    ProgramCtl.save(prog)