import socket
import json
import vgamepad as vg
import keyboard
import math
import threading
gamepad_p1 = None
gamepad_p2 = None

def get_stick_value(stickValue):
    if stickValue == 0 or stickValue == -0:
        return stickValue
    newValue = round(2 * math.floor(abs(stickValue) / 18) / 10 * (stickValue/abs(stickValue)), 1)
    return min(max(newValue, -1), 1)

def gamepad_controller(gamepad, data):
    data_splited = data.split(" ")
    leftStickX, leftStickY, rightStickY, m5buttonClick = int(data_splited[1]) - 100, int(data_splited[2]) - 100, int(data_splited[3]) - 100, int(data_splited[4])
    floatLeftStickX = get_stick_value(leftStickX) * -1
    floatLeftStickY = get_stick_value(leftStickY)
    floatRightStickY = get_stick_value(rightStickY)
    gamepad.left_joystick_float(x_value_float=floatLeftStickX, y_value_float=floatLeftStickY)
    print(floatLeftStickX, floatLeftStickY)

    if floatRightStickY > 0.5:
        gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP)
    else:
        gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP)
    if floatRightStickY < 0.5:
        gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN)
    else:
        gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN)
    if m5buttonClick == 1:
        gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
    else:
        gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)

    gamepad.update()  # Send the updated state to the gamepad


def handle_client(conn, addr):
    global gamepad_p1
    global gamepad_p2
    with conn:
        print(f"Connected by {addr}")
        old_data_p1, old_data_p2 = "", ""
        data_p1, data_p2 = "", ""

        while True:
            try:
                received_bytes = conn.recv(1024)  # Adjust the buffer size as needed
                if not received_bytes:
                    break
                
                gamepad_data = received_bytes.decode()

                for input in gamepad_data.split(";"):
                    if not input == "":
                        user = input.split(" ")[0]

                        if user == "P1":
                            if gamepad_p1 == None:
                                gamepad_p1 = vg.VX360Gamepad()

                            data_p1 = input
                        elif user == "P2":
                            if gamepad_p2 == None:
                                gamepad_p2 = vg.VX360Gamepad()
                                
                            data_p2 = input

                        if old_data_p1 != data_p1:
                            gamepad_controller(gamepad_p1, data_p1)
                            old_data_p1 = data_p1
                        
                        if old_data_p2 != data_p2:
                            gamepad_controller(gamepad_p2, data_p2)
                            old_data_p2 = data_p2

            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
                break


def main():
    host = '0.0.0.0'
    port = 12346

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((host, port))
            s.listen()

            print(f"Waiting for connection on {host}:{port}")            

            while True:
                conn, addr = s.accept()
                conn.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 2048)  # Set buffer size to 8 KB
                print(addr)
                
                cancel_flag = threading.Event()

                with conn:
                    threading.Thread(target=handle_client, args=(conn, addr)).start()

                    while not cancel_flag.is_set():
                        new_conn, _ = s.accept()
                        new_conn.close()
                        cancel_flag.set()

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()