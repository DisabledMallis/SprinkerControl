from nicegui import ui

class Zone:
    def __init__(self, zone: int):
        self.zone = zone
    
    def valid(self) -> bool:
        return self.zone > 0 and self.zone < 5
    
    def start(self) -> bool:
        if self.valid():
            ui.notify(f"Started zone #{self.id()}")
        else:
            ui.notify(f"Failed to start zone #{self.id()}")
        return self.valid()
    
    def stop(self) -> bool:
        if self.valid():
            ui.notify(f"Stopped zone #{self.id()}")
        else:
            ui.notify(f"Failed to stop zone #{self.id()}")
        return self.valid()
    
    def id(self) -> int:
        return self.zone

class ZoneTask:
    def __init__(self, zone: Zone, duration: int):
        self.zone = zone
        self.duration = duration
        self.remaining = duration
    
    def get_zone(self) -> Zone:
        return self.zone

    def get_time_remaining(self) -> int:
        return self.remaining
    
    def expired(self) -> bool:
        return self.remaining <= 0
    
    def update(self):
        if not self.expired():
            # If its the first update, start the zone
            if self.duration == self.remaining:
                self.zone.start()

            self.remaining -= 1
        
        # If its expired, stop the zone
        if self.expired():
            self.zone.stop()
    
class ZoneCtl:
    def __init__(self):
        self.zones = [Zone(zone) for zone in range(1, 5)]
        self.zone_queue = []
    
    def has(self, zone: int) -> bool:
        return len(self.zones) > zone-1 and zone > 0

    def get(self, zone: int) -> Zone:
        if self.has(zone):
            return self.zones[zone-1]
        return None
    
    def queue(self, zone: Zone, duration: int):
        self.zone_queue.append(ZoneTask(zone, duration))

    def get_zones(self) -> list[Zone]:
        return self.zones

    def get_tasks(self):
        return self.zone_queue
    
    def has_tasks(self):
        return self.count_tasks() > 0
    
    def count_tasks(self):
        return len(self.zone_queue)

    # Stops all zones & clears the queue
    def clear(self):
        self.zone_queue.clear()
        for zone in self.zones:
            zone.stop()

    def update(self):
        if not self.has_tasks():
            return
        
        self.zone_queue[0].update()
        self.zone_queue = [task for task in self.zone_queue if not task.expired()]