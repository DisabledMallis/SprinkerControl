MESSAGE_INVALID = -1
MESSAGE_BOOT = 'I'
MESSAGE_BEGIN = 'B'
MESSAGE_END = 'E'
MESSAGE_OK = 'O'
MESSAGE_ERROR = 'X'
MESSAGE_PING = 'P'
MESSAGE_PONG = 'L'

serial_port = "/dev/ttyUSB0"
baude = 9600

import serial
import os
import time
class SpkrCtl:
    def __init__(self):
        self.serial = serial.Serial(serial_port, baudrate=baude)
        self.properly_connected = False

    def connect(self) -> bool:
        while not self.serial.is_open:
            self.serial = serial.Serial(serial_port, baudrate=baude)
        try:
            self.send(MESSAGE_PING)
            while not self.recv().startswith(MESSAGE_PONG):
                self.send(MESSAGE_PING)
            self.properly_connected = True
            return True
        except:
            return False

    def is_port_open(self) -> bool:
        return os.path.exists(serial_port)

    def is_connected(self) -> bool:
        return self.serial.is_open and self.is_port_open()

    def is_properly_connected(self) -> bool:
        return self.is_connected() and self.properly_connected

    def disconnect(self):
        self.serial.close()

    def send(self, msg: str) -> bool:
        try:
            self.serial.write(msg.encode(encoding='ascii'))
            print(f"SEND: {msg}")
            return True
        except Exception as e:
            print(f"FAIL! {e}")
            self.serial.close()
        return False

    def available(self):
        return self.serial.in_waiting

    def recv(self):
        return self.serial.read_until().decode(encoding='ascii')

spkr_ctl: SpkrCtl = None