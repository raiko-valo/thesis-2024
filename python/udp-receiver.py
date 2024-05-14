import socket
import json
import vgamepad as vg
import math

# Function to normalize joystick values to the range [-1, 1]
def get_stick_value(stickValue):
    if stickValue == 0 or stickValue == -0:
        return stickValue
    newValue = round(2 * math.floor(abs(stickValue) / 18) / 10 * (stickValue/abs(stickValue)), 1)
    return min(max(newValue, -1), 1)

# Function to control the gamepad based on received input data
def gamepad_controller(gamepad, data, controller_type = ""):
    data_splited = data.split(" ")
    leftStickX, leftStickY, rightStickY, m5buttonClick = int(data_splited[0]) - 100, int(data_splited[1]) - 100, int(data_splited[2]) - 100, int(data_splited[3])
    floatLeftStickX = get_stick_value(leftStickX) * -1
    floatLeftStickY = get_stick_value(leftStickY) * -1
    floatRightStickY = get_stick_value(rightStickY)
    gamepad.left_joystick_float(x_value_float=floatLeftStickX, y_value_float=floatLeftStickY)

    if controller_type == "ds4":    
        if floatRightStickY > 0.5:
            gamepad.directional_pad(direction=vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_NORTH)
        elif floatRightStickY < -0.5:
            gamepad.directional_pad(direction=vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_SOUTH)
        else:
            gamepad.directional_pad(direction=vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_NONE)
        if m5buttonClick == 1:
            gamepad.press_button(button=vg.DS4_BUTTONS.DS4_BUTTON_CROSS)
        else:
            gamepad.release_button(button=vg.DS4_BUTTONS.DS4_BUTTON_CROSS)
    elif controller_type == "xbox" or controller_type == "":
        if floatRightStickY > 0.5:
            gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP)
        else:
            gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP)
        if floatRightStickY < -0.5:
            gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN)
        else:
            gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN)
        if m5buttonClick == 1:
            gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
        else:
            gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)

    gamepad.update()  # Send the updated state to the gamepad

# Function to send data over UDP
def send_data(message, player, port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    client_socket.sendto(message.encode('utf-8'), (player, port))
    client_socket.close()

# Function to start the UDP server
def start_server(host, port):
    # Create a UDP socket and configure it
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((host, port))
    print(f"Server listening on {host}:{port}")

    # Dictionary to store gamepads
    gamepads = {}
    is_exit = False

    # Continuous loop to receive data
    while True:
        data, address = server_socket.recvfrom(1024)
        data_decoded = data.decode('utf-8')

        if is_exit:
            break

        for input in data_decoded.split(";"):
            if input.strip():
                action = json.loads(input)

                if "type" not in action or action["type"] == "input":
                    player = action["player"]

                    # Initialize gamepad if not present
                    if player not in gamepads.keys():
                        if "controller" not in action or action["controller"] == "xbox":
                            gamepads[player] = vg.VX360Gamepad()
                        elif action["controller"] == "ds4":
                            gamepads[player] = vg.VDS4Gamepad()

                    elif player == "exit":
                        is_exit = True
                        break

                    # Handle test action
                    if "type" in action and action["type"] == "test" and "send_time" in action.keys():
                        action["type"] = "time"
                        ip_parts = HOST.split('.')
                        ip_parts[-1] = player
                        ip_address = '.'.join(ip_parts)
                        dataStr = json.dumps(action) + ";"
                        send_data(dataStr, ip_address, PORT)

                    # Control gamepad based on input data
                    if "controller" in action:
                        gamepad_controller(gamepads[player], action["data"], action["controller"])
                    else:
                        gamepad_controller(gamepads[player], action["data"])

                if action["type"] == "time":
                    dataStr = input + ";"
                    send_data(dataStr, '192.168.0.79', PORT)


# Function to get the local IP address
def get_ip_address():
    try:
        # Create a socket object
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Connect to any remote server (we don't actually need to send data)
        s.connect(("8.8.8.8", 80))
        # Get the local IP address
        ip_address = s.getsockname()[0]
        # Close the socket
        s.close()
        return ip_address
    except Exception as e:
        print("Error:", e)
        return None

if __name__ == "__main__":
    PORT = 12345 
    HOST = get_ip_address()
    if HOST != None:
        start_server(HOST, PORT)
