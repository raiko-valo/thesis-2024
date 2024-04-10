import socket
import keyboard
import time
import json
import threading
import math

PORT = 12345 

# def send_data(host, port, message):
#     client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#     client_socket.sendto(message.encode('utf-8'), (host, port))
#     client_socket.close()

def get_ip_address():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_address = s.getsockname()[0]
        s.close()
        return ip_address
    except Exception as e:
        print("Error:", e)
        return None

def send_data(player, data = ''):
    send_time = int(time.time() * TIME_MODIFIER)
    message = {'player':player,'data':data,'send_time':send_time,'type': "input"}
    message_str = json.dumps(message) + ";"
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.sendto(message_str.encode('utf-8'), (HOST, PORT))
    client_socket.close()


def handle_controls():
    last_data_p1 = "100 100 100 0"
    last_data_p2 = "100 100 100 0"

    while True:
        # Initialize player data
        key_pressed_p1 = ""
        key_pressed_p2 = ""

        # Player 1 controls
        if keyboard.is_pressed('a') and not keyboard.is_pressed('d'):  # Left
            key_pressed_p1 += "0"
        elif keyboard.is_pressed('d') and not keyboard.is_pressed('a'): # Right
            key_pressed_p1 += "200"
        else:
            key_pressed_p1 += "100"
        
        if keyboard.is_pressed('w') and not keyboard.is_pressed('s'):  # Up
            key_pressed_p1 += " 200"
        elif keyboard.is_pressed('s') and not keyboard.is_pressed('w'):  # Down
            key_pressed_p1 += " 0"
        else:
            key_pressed_p1 += " 100"

        if keyboard.is_pressed('x') and not keyboard.is_pressed('c'):  # Up
            key_pressed_p1 += " 200"
        elif keyboard.is_pressed('c') and not keyboard.is_pressed('x'):  # Down
            key_pressed_p1 += " 0"
        else:
            key_pressed_p1 += " 100"
        
        if keyboard.is_pressed('z'):  # a
            key_pressed_p1 += " 1"
        else:
            key_pressed_p1 += " 0"

        # Player 2 controls
        if keyboard.is_pressed('j') and not keyboard.is_pressed('l'):  # Left
            key_pressed_p2 += "0"
        elif keyboard.is_pressed('l') and not keyboard.is_pressed('j'): # Right
            key_pressed_p2 += "200"
        else:
            key_pressed_p2 += "100"
        
        if keyboard.is_pressed('i') and not keyboard.is_pressed('k'):  # Up
            key_pressed_p2 += " 200"
        elif keyboard.is_pressed('k') and not keyboard.is_pressed('i'):  # Down
            key_pressed_p2 += " 0"
        else:
            key_pressed_p2 += " 100"

        if keyboard.is_pressed('n') and not keyboard.is_pressed('m'):  # Up
            key_pressed_p2 += " 200"
        elif keyboard.is_pressed('m') and not keyboard.is_pressed('n'):  # Down
            key_pressed_p2 += " 0"
        else:
            key_pressed_p2 += " 100"
        
        if keyboard.is_pressed(','):  # a
            key_pressed_p2 += " 1"
        else:
            key_pressed_p2 += " 0"

        if keyboard.is_pressed('e'):
            send_data('exit')
            break

        data_p1 = "".join(key_pressed_p1)
        data_p2 = "".join(key_pressed_p2)

        if data_p1 != last_data_p1:
            send_data('1', data_p1)
            last_data_p1 = data_p1

        if data_p2 != last_data_p2:
            send_data('2', data_p2)
            last_data_p2 = data_p2

        time.sleep(0.01)


def listen_on_port():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((HOST, PORT+1))
    print(f"Server listening on {HOST}:{PORT+1}")
    while True:
        data, address = server_socket.recvfrom(1024)
        if (data):
            data_decoded = data.decode('utf-8')
            recieve_time = int(time.time() * TIME_MODIFIER)

            for input in data_decoded.split(";"):
                if input.strip():
                    action = json.loads(input)
                    print(action)

                    if action["type"] == "time":
                        if "recieve_time" not in action.keys():
                            time_spent = recieve_time - int(action["send_time"])
                            action["recieve_time"] = recieve_time
                        else:
                            time_spent = int(action["recieve_time"]) - int(action["send_time"])

                        action["time_spent"] = time_spent
                        action["average_time"] = math.ceil(time_spent/2)

                        break

                        with open("delta_test.txt", "a") as file:
                            file.write(json.dumps(action) + "\n")


        

if __name__ == "__main__":
    TIME_MODIFIER = 10000
    HOST = get_ip_address()
    
    listen_thread = threading.Thread(target=listen_on_port, args=())
    listen_thread.start()

    # handle_controls()
