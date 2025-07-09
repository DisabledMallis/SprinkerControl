MESSAGE_PING = 'P'
MESSAGE_BOOT = 'B'
MESSAGE_ZONE = 'Z'
MESSAGE_END = 'E'
MESSAGE_OK = 'O'
MESSAGE_ERROR = 'X'

serial_ports = ["/dev/ttyUSB0", "/dev/ttyUSB1", "/dev/ttyUSB2", "/dev/ttyUSB3", "/dev/cu.usbserial-110", "/dev/cu.usbserial-120", "/dev/cu.usbserial-130", "/dev/cu.usbserial-140"]
baude = 9600

import os
def find_serial_port() -> str:
    for port in range(0, len(serial_ports)):
        if os.path.exists(serial_ports[port]):
            return serial_ports[port]
    return None

import serial
class Connection:
    def __init__(self):
        self.conn = serial.Serial()
        self.conn.write_timeout = 5
        self.conn.read_timeout = 5
        self.initialized = False
    
    # Sanitize state (ig)
    def _sanitize_state(self):
        if not self.connected():
            self.initialized = False

    # Connect to the USB device
    def connect(self, timeout=5) -> bool:
        try:
            delay = 0.5
            attempts = timeout * (1.0 / delay)
            while not self.connected() and attempts > 0:
                self.port = find_serial_port()
                print(f"(ConnCtl) [*] Connecting to device on: {self.port} ({attempts} attempts remaining)")
                self.conn = serial.Serial(port=self.port, baudrate=baude)
                time.sleep(delay)
                attempts -= 1
            return self.connected()
        except Exception as e:
            print(f"(ConnCtl) [!] Connection failed: {e}")
        return False

    def port_valid(self) -> bool:
        return os.path.exists(self.port)

    def connected(self) -> bool:
        return self.conn.is_open and self.port_valid()

    # Initialize communication protocol
    def initialize(self, timeout=5) -> bool:
        delay = 0.5
        attempts = timeout * (1.0 / delay)
        while self.connected() and not self.initialized:
            self.println(MESSAGE_PING)
            print(f"(ConnCtl) [>] {MESSAGE_PING}")
            while self.available() > 0:
                response = self.read()
                print(f"(ConnCtl) [<] {response}")
                if response.startswith(MESSAGE_PING):
                    self.initialized = True
            attempts -= 1
            time.sleep(delay)
        return self.is_initialized()

    def is_initialized(self) -> bool:
        self._sanitize_state()
        return self.initialized and self.connected()

    def available(self):
        if not self.connected():
            return 0
        return self.conn.in_waiting

    def println(self, msg) -> bool:
        if not self.connected():
            return False
        self.conn.write(f"{msg}\n".encode(encoding='ascii'))
        self.conn.flush()

    def read(self) -> str:
        if not self.connected():
            return ""
        try:
            return self.conn.read_until().decode(encoding='ascii')
        except UnicodeDecodeError as ude:
            print(f"(SpkrCtl) [!] {e}")
            return MESSAGE_ERROR

class SpkrCtl:
    def __init__(self):
        self.conn = Connection()
    
    def initialize(self, timeout=5) -> bool:
        print("(SpkrCtl) [*] Connecting...")
        if not self.conn.connect(timeout=timeout):
            print("(SpkrCtl) [!] Connection failed! Is the device plugged in?")
            return False

        print("(SpkrCtl) [*] Initializing...")
        if not self.conn.initialize(timeout=timeout):
            print("(SpkrCtl) [!] Failed to initialize! Is this the correct device?")
            return False

        print("(SpkrCtl) [*] Protocol initialized!")
        return self.initialized()

    def initialized(self) -> bool:
        return self.conn.is_initialized()

    def zone(self, zone: int, timeout=5) -> bool:
        if not self.initialized():
            print(f"(SpkrCtl) [!] Cannot start zone {zone}, SpkrCtl is NOT initialized!")
            return False

        print(f"(SpkrCtl) [*] Starting zone #{zone}...")
        delay = 0.25
        attempts = timeout * (1.0 / delay)
        while not self.conn.available() > 0 and attempts > 0:
            self.conn.println(f"{MESSAGE_ZONE}{zone}")
            print(f"(SpkrCtl) [.] Zone command sent")
            time.sleep(delay)
            attempts -= 1

        attempts = timeout * (1.0 / delay)
        total_attempts = attempts
        while attempts > 0:
            msg = self.conn.read()
            if msg.startswith(MESSAGE_OK):
                print(f"(SpkrCtl) [✅] Zone {zone} started!")
                return True
            elif msg.startswith(MESSAGE_ERROR):
                print(f"(SpkrCtl) [!] {msg}")
                return False
            else:
                print(f"(SpkrCtl) [?] Unknown response: {msg}")
            attempts -= 1
            time.sleep(delay)
        print(f"(SpkrCtl) [!] Failed to start zone #{zone} after {total_attempts} attempts!")
        return False
    
    def end(self, timeout=5) -> bool:
        if not self.initialized():
            print(f"(SpkrCtl) [!] Cannot stop zones, SpkrCtl is NOT initialized!")
            return False

        delay = 0.25
        attempts = timeout * (1.0 / delay)
        while not self.conn.available() > 0 and attempts > 0:
            self.conn.println(MESSAGE_END)
            time.sleep(delay)
            attempts -= 1

        if attempts <= 0:
            print(f"(SpkrCtl) [!] Cannot stop zones, no response received!")
            return False

        attempts = timeout * (1.0 / delay)
        while attempts > 0:
            msg = self.conn.read()
            if msg.startswith(MESSAGE_OK):
                print(f"(SpkrCtl) [✅] Zones ended!")
                return True
            elif msg.startswith(MESSAGE_ERROR):
                print(f"(SpkrCtl) [!] {msg}")
                return False
            attempts -= 1
            time.sleep(delay)
        return False

    def ping(self, timeout=5) -> bool:
        if not self.initialized():
            print(f"(SpkrCtl) [!] Cannot ping, SpkrCtl is NOT initialized!")
            return False

        delay = 0.25
        attempts = timeout * (1.0 / delay)
        while not self.conn.available() > 0 and attempts > 0:
            self.conn.println(MESSAGE_PING)
            time.sleep(delay)
            attempts -= 1
        
        if attempts <= 0:
            print(f"(SpkrCtl) [!] No ping response received!")
            return False

        attempts = timeout * (1.0 / delay)
        while attempts > 0 and self.conn.available() > 0:
            msg = self.conn.read()
            success = False
            while msg.startswith(MESSAGE_PING) and self.conn.available() > 0:
                print(f"(SpkrCtl) [.] Ping!")
                msg = self.conn.read()
            print(f"(SpkrCtl) [.] NO Ping!")
            attempts -= 1
            time.sleep(delay)
        return True


spkr_ctl = SpkrCtl()

import time
if __name__ == "__main__":
    print("[*] Starting SpkrCtl terminal...")
    if not spkr_ctl.initialize():
        print("[!] Failed to initialize spkr_ctl!")
    if spkr_ctl.initialized():
        print("[✅] Initialized spkr_ctl!")
    
    cmd = None
    while spkr_ctl.initialized():
        cmd = input(">")
        spkr_ctl.ping()
        if cmd[0] == MESSAGE_ZONE and len(cmd) > 1 and cmd[1].isdigit():
            spkr_ctl.zone(int(cmd[1]))
        elif cmd[0] == MESSAGE_END:
            spkr_ctl.end()
        elif cmd[0] == MESSAGE_PING:
            spkr_ctl.ping()
        else:
            print("[!] Unknown command! P = Ping, Z# = start a zone by #, E = end all zones")
    
    print("[✅] Connection closed, exiting!")

