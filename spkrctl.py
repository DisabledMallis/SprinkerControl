MESSAGE_INVALID = -1
MESSAGE_BOOT = 'I'
MESSAGE_BEGIN = 'B'
MESSAGE_END = 'E'
MESSAGE_OK = 'O'
MESSAGE_ERROR = 'X'
MESSAGE_PING = 'P'
MESSAGE_PONG = 'L'

serial_ports = ["/dev/ttyUSB0", "/dev/ttyUSB1", "/dev/ttyUSB2", "/dev/ttyUSB3"]
baude = 9600

def find_serial_port() -> str:
    for port in range(0, 4):
        if os.path.exists(serial_ports[port]):
            return serial_ports[port]
    return None

import serial
import os
import time
import queue

class SpkrCtl:
    def __init__(self):
        self.serial = serial.Serial(find_serial_port(), baudrate=baude, write_timeout=5)
        self.properly_connected = False
        self.send_queue = queue.Queue()
        self.recv_queue = queue.Queue()

    def connect(self) -> bool:
        if not self.serial.is_open:
            self.serial = serial.Serial(find_serial_port(), baudrate=baude)

    def is_port_open(self) -> bool:
        return find_serial_port() != None

    def is_connected(self) -> bool:
        return self.serial.is_open and self.is_port_open()

    def is_properly_connected(self) -> bool:
        return self.is_connected() and self.properly_connected

    def disconnect(self):
        self.serial.close()

    def send(self, msg: str) -> bool:
        self.send_queue.put(msg)
        return True
        
        """ try:
            self.serial.write(msg.encode(encoding='ascii'))
            print(f"SEND: {msg}")
            return True
        except Exception as e:
            print(f"FAIL! {e}")
            self.serial.close()
        return False """

    def available(self):
        return self.serial.in_waiting

    def recv(self) -> str:
        if self.recv_queue.empty():
            return None
        return self.recv_queue.get()
        """ return self.serial.read_until().decode(encoding='ascii') """

    def update(self):
        if not self.is_port_open():
            self.properly_connected = False
            return
        if not self.is_connected():
            self.properly_connected = False
            return self.connect()
        if not self.is_properly_connected():
            self.serial.write(MESSAGE_PING.encode(encoding='ascii'))
            received = self.serial.read_until().decode(encoding='ascii')
            if received.startswith(MESSAGE_PONG):
                self.properly_connected = True
                return

        if self.serial.in_waiting > 0:
            received = self.serial.read_until()
            if received.startswith(MESSAGE_BOOT):
                self.properly_connected = False
                print("DEVICE BOOTING!")
                return
            self.recv_queue.put(received)

        if not self.send_queue.empty and self.is_properly_connected():
            self.serial.write(self.send_queue.get().encode(encoding='ascii'))

spkr_ctl: SpkrCtl = None