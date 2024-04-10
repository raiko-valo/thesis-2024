#include "JoyC.h"
#include "M5StickC.h"
#include <WiFi.h>
#include <WiFiUdp.h>
#include <ArduinoJson.h>

JoyC joyc;
TFT_eSprite img = TFT_eSprite(&M5.Lcd);

uint8_t show_flag = 0;
String joystickValues; // Global variable to store joystick values
String lastInput = "";

WiFiUDP udp;
WiFiUDP udpListener; // UDP object for listening
const int listenerPort = 1111; // Port for UDP listening

const char *ssid = "poco_wifi";
const char *password = "1122qqww";
const char *host = "192.168.39.141";
const int port = 12345;  // Replace with your server port

StaticJsonDocument<200> outboundData; // JSON document buffer
String localIPAddress;

void setup() {
    M5.begin();
    Wire.begin(0, 26, 400000UL);
    img.createSprite(80, 160);

    Serial.begin(115200);

    // Connect to WiFi
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
        delay(1000);
        Serial.println("Connecting to WiFi...");
    }

    Serial.println("Connected to WiFi");

    // Extract numbers after last dot
    localIPAddress = WiFi.localIP().toString();
    int lastDotIndex = localIPAddress.lastIndexOf('.');
    localIPAddress = localIPAddress.substring(lastDotIndex + 1);
    
    // Begin UDP communication
    udp.begin(port);
}

int lastLeftStickX = 0;
int lastLeftStickY = 0;
int lastrightStickY = 0;
int lastM5ButtonClick = 0;

void sendData(String message) {
    udp.beginPacket(host, port);
    Serial.println(message);
    udp.print(message);
    udp.endPacket();
}

void loop() {
    char text_buff[100];

    M5.update();
    img.fillSprite(TFT_BLACK);

    int leftStickX = joyc.GetX(0);
    int leftStickY = joyc.GetY(0);
    int rightStickY = joyc.GetY(1);
    int m5ButtonClick = 0;
    if (M5.BtnA.isPressed()) {
        m5ButtonClick = 1;
    }

    if (leftStickX != lastLeftStickX || 
        leftStickY != lastLeftStickY ||
        rightStickY != lastrightStickY ||
        lastM5ButtonClick != m5ButtonClick) {

        joystickValues = String(leftStickX) + " " + String(leftStickY) + " " + String(rightStickY) + " " + String(m5ButtonClick);

        // Display left stick values
        img.drawCentreString("Left Stick", 40, 6, 1);
        sprintf(text_buff, "X: %d", leftStickX);
        img.drawCentreString(text_buff, 40, 20, 1);
        sprintf(text_buff, "Y: %d", leftStickY);
        img.drawCentreString(text_buff, 40, 34, 1);

        // Display right stick values
        img.drawCentreString("Right Stick", 40, 62, 1);
        sprintf(text_buff, "Y: %d", rightStickY);
        img.drawCentreString(text_buff, 40, 76, 1);
        sprintf(text_buff, "Button: %d", m5ButtonClick);
        img.drawCentreString(text_buff, 40, 90, 1);

        img.pushSprite(0, 0);


        // Format data as JSON
        outboundData.clear();
        outboundData["player"] = localIPAddress;
        outboundData["type"] = "input";
        outboundData["data"] = joystickValues;
        outboundData["send_time"] = millis(); // Current time in milliseconds
        
        // Serialize JSON to a string
        String outboundJson;
        serializeJson(outboundData, outboundJson);


        sendData(outboundJson);

        lastLeftStickX = leftStickX;
        lastLeftStickY = leftStickY;
        lastrightStickY = rightStickY;
        lastM5ButtonClick = m5ButtonClick;
    }


    int packetSize = udp.parsePacket();
    if (packetSize > 0) {
        Serial.println(packetSize);
        // Received a packet
        String receivedData = "";
        while (udp.available()) {
            char incomingChar = udp.read();
            receivedData += incomingChar;
        }
        
        const size_t capacity = JSON_OBJECT_SIZE(2) + 30;
        DynamicJsonDocument inboundData(capacity);

        // Parse received data into JSON
        DeserializationError error = deserializeJson(inboundData, receivedData);
        if (error) {
            Serial.print("deserializeJson() failed: ");
            Serial.println(error.c_str());
            return;
        }

        inboundData["receive_time"] = millis();
        String inboundJson;
        serializeJson(inboundData, inboundJson);

        sendData(inboundJson);
    }
}
