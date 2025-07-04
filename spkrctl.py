MESSAGE_INVALID = -1
MESSAGE_BOOT = b'I'
MESSAGE_BEGIN = b'B'
MESSAGE_END = b'E'
MESSAGE_OK = b'O'
MESSAGE_ERROR = b'X'
MESSAGE_PING = b'P'
MESSAGE_PONG = b'L'

serial_port = "/dev/cu.usbmodemRFCX314G4TL2"
baude = 9600

import serial
class SpkrCtl:
    def __init__(self):
        self.serial = serial.Serial(serial_port, baudrate=baude)
        self.properly_connected = False

    def connect(self) -> bool:
        while not self.serial.is_open:
            self.serial = serial.Serial(serial_port, baudrate=baude)
        try:
            self.send(MESSAGE_PING)
            if not self.recv() == MESSAGE_PONG:
                return False
            self.properly_connected = True
            return True
        except:
            return False

    def is_connected(self) -> bool:
        return self.serial.is_open

    def is_properly_connected(self) -> bool:
        return self.is_connected() and self.properly_connected

    def disconnect(self):
        self.serial.close()

    def send(self, msg) -> bool:
        try:
            self.serial.write(msg)
            print(f"SEND: {msg}")
            return True
        except:
            print("FAIL!")
            self.serial.close()
        return False

    def recv(self, size=1):
        return self.serial.read(size)