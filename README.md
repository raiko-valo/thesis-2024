# Thesis 2024

This codebase is developed as a part of thesis, and it is about developing system to control game with M5StickC + JoyC controller that is sending gamepad inputs over WiFi connection to the game host machine. This involves a controller and a receiver script, the client is sending gamepad input data through local network connection to the server code, that is relying those to game by emulating virtual gamepad.

----

## Setup

After forking repository, dependent library needs to be installed, do it with:
```
pip install vgamepad
```
To program ESP32 you need Arduino IDE or PlatformIO extension in VSCode. For ESP32 to connect with receiver, `ssid` and `password` values in `main.cpp` must be configured to match your network information. Variable `host` changed to match with receiver ip. This done, ESP32 should connect to WiFi and be able to send information to the server.

----
