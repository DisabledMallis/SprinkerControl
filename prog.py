from datetime import time, datetime
from zonectl import ZoneTask
import json

days = ['M', 'T', 'W', 'R', 'F', 'S', 'U']
class Program:
    def __init__(self, name="Unnamed Program", days=days, start_time="06:00", tasks=[]):
        self.name = name
        self.days = days
        self.start_time = start_time
        self.tasks = tasks
        self.run_now = False
    
    def filename(self) -> str:
        return f"{self.name.lower().replace(' ', '_')}.json"

    def to_json(self):
        return json.dumps(
            self,
            default=lambda o: o.__dict__, 
            sort_keys=True,
            indent=4)
    
    @classmethod
    def from_json(cls, json_str):
        data = json.loads(json_str)
        return cls(
            name=data.get("name", "Unnamed Program"),
            days=data.get("days", []),
            start_time=data.get("start_time", "06:00"),
            tasks=data.get("tasks", [])
        )

import os
class ProgramCtl:
    def __init__(self):
        self.reload()

    def add(self, prog: Program) -> bool:
        self.programs.append(prog)

    def remove(self, prog: Program):
        if prog is None:
            return
        os.remove(f"programs/{prog.filename()}")
        self.programs.remove(prog)
    
    def get(self, name: str) -> Program:
        for prog in self.programs:
            if prog.name == name:
                return prog
        return None

    def reload(self):
        self.programs = []

        if not os.path.exists('programs'):
            os.mkdir('programs')
        
        for prog_json in os.listdir('programs'):
            path = f"programs/{prog_json}"
            if os.path.isfile(path):
                print(f"Loading program '{prog_json}'")
                with open(path) as f:
                    self.add(Program.from_json(f.read()))

    @classmethod
    def save(cls, prog: Program) -> bool:
        if not os.path.exists('programs'):
            os.mkdir('programs')
        
        file = prog.filename()
        print(f"Saving {file}")
        with open(f"programs/{file}", 'w') as w:
            w.write(prog.to_json())

if __name__ == "__main__":
    prog_ctl = ProgramCtl()
    for prog in prog_ctl.programs:
        print(prog.to_json())