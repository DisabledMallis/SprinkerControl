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

    def connect(self) -> bool:
        while not self.serial.is_open:
            self.serial = serial.Serial(serial_port, baudrate=baude)
        try:
            self.send(MESSAGE_PING)
            if not self.recv() == MESSAGE_PONG:
                return False
            return True
        except:
            return False

    def is_connected(self):
        return self.serial.is_open

    def disconnect(self):
        self.serial.close()

    def send(self, msg):
        try:
            self.serial.write(msg)
            print(f"SEND: {msg}")
        except:
            print("FAIL!")
            self.serial.close()

    def recv(self, size=1):
        return self.serial.read(size)