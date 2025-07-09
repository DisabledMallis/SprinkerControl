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
def connect_serial():
    conn = serial.Serial(port=find_serial_port(), baudrate=baude)
    conn.write_timeout = 5
    return conn

import threading
import time
import zonectl

last_error: str = None
running_spkr = True
spkr_connected = False
def spkr_runner():
    global running_spkr
    global last_error
    global spkr_connected

    conn = connect_serial()
    while running_spkr:
        # Delay 1s
        time.sleep(1.0)

        if not conn.is_open:
            spkr_connected = False
            conn = connect_serial()
            continue
        elif not spkr_connected:
            spkr_connected = True
            print("(SpkrCtl) [✅] Connected!")

        try:
            if zonectl.active_zone < 1 or zonectl.active_zone > 4:
                conn.write(MESSAGE_END.encode(encoding='ascii'))
                print(f"(SpkrCtl) [.] sending zone end message")
            else:
                conn.write(f"{MESSAGE_ZONE}{zonectl.active_zone}".encode(encoding='ascii'))
                print(f"(SpkrCtl) [.] sending zone {zonectl.active_zone} message")
        except serial.SerialException as se:
            # If there is a connection issue, reconnect
            print(se)
            conn = connect_serial()
        
        try:
            while conn.in_waiting > 0:
                try:
                    msg = conn.read_until().decode(encoding='ascii')
                    if msg.startswith(MESSAGE_ERROR):
                        last_error = msg
                    elif msg.startswith(MESSAGE_OK):
                        continue
                    else:
                        print(f"Unknown message: {msg}")
                except Exception as e:
                    print(e)
        except Exception as e:
            # Theres usually an exception with conn.in_waiting when unplugged
            print(e)
            conn = connect_serial()
        

spkr_thread = threading.Thread(target=spkr_runner)

if __name__ == "__main__":
    spkr_thread.start()
    while running_spkr:
        try:
            cmd = input(">")
        except KeyboardInterrupt:
            running_spkr = False
            continue
        if cmd.startswith(MESSAGE_ZONE) and len(cmd) > 1:
            try:
                active_zone = int(cmd[1])
                print(f"Starting zone #{active_zone}")
            except:
                print(f"Invalid zone '{cmd[1]}'")
                active_zone = -1
        elif cmd.startswith(MESSAGE_END):
            print("Ending zones")
            active_zone = -1
        else:
            print("Unknown command")