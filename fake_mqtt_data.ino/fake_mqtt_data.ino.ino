#define BOARD_TYPE  "ESP32"
#include "arduino_secrets.h" // enter secret wifi ssid and passwd in this file
#include <WiFi.h>
#include <PubSubClient.h>
#include <WiFiMulti.h>

const char* ssid = SECRET_SSID;
const char* password = SECRET_PASS;
const char* ssid2 = SECRET_SSID2;
const char* password2 = SECRET_PASS2;
const char* mqttuser = SECRET_MQTTUSER;
const char* mqttpass = SECRET_MQTTPASS;

const char* mqtt_server = "mqtt.cetools.org";
const int mqtt_port = 1884;

// Set up WiFi and MQTT clients
WiFiMulti wifiMulti;
WiFiClient espClient;
PubSubClient client(espClient);


void setup() {
    // Start the hardware serial.
    Serial.begin(9600);
    // Ensure WiFi is in station mode not AP mode
    WiFi.mode(WIFI_STA);
// Register multiple networks
    wifiMulti.addAP(SECRET_SSID, SECRET_PASS);
    if (strlen(SECRET_SSID2) > 0 && strlen(SECRET_PASS2) > 0) {
        wifiMulti.addAP(SECRET_SSID2, SECRET_PASS2);
    }

    // Check to see if connected and wait until you are
    while (wifiMulti.run() != WL_CONNECTED) {
        delay(500);
        Serial.println("Connecting to WiFi...");
    }
    Serial.println("WiFi connected");
    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());

    // Connect to MQTT server
    client.setServer(mqtt_server, mqtt_port);

    while (!client.connected()) {
        String clientId = "ESP32Client-";
        clientId += String(WiFi.macAddress());
        Serial.printf("The client %s connects to the MQTT broker\n", clientId.c_str());

        if (client.connect(clientId.c_str(), SECRET_MQTTUSER, SECRET_MQTTPASS)) {
            Serial.println("MQTT broker connected");
            client.subscribe("student/ucbvren/headsets/headset2");
        } else {
            Serial.print("failed with state ");
            Serial.print(client.state());
            delay(2000);
        }
    }
}

void loop() {
    // Manually create fake brain data
     // The .readCSV() function returns a string (well, char*) listing the most recent brain data, in the following format:
    // "signal strength, attention, meditation, delta, theta, low alpha, high alpha, low beta, high beta, low gamma, high gamma"
    int signalStrength = 0;  // Signal strength
    //int meditation = 60;
    int meditation = random(80, 100); // Random meditation level between 20 and 100
    String brainData = String(signalStrength) + ",0," + String(meditation) + ",0,0,0,0,0,0,0,0";
    
    Serial.println(brainData);
    
    // Convert the brainData to a char array for MQTT publishing
    char msg[brainData.length() + 1];
    brainData.toCharArray(msg, brainData.length() + 1);
    
    // Publish the fake data to the MQTT topic
    client.publish("student/ucbvren/headsets/headset2", msg);
    delay(1000); // Replicate the headset data transmission rate


    // Maintain MQTT connection
    if (!client.connected()) {
        reconnect();
    }
    client.loop();
}

// Function to reconnect to MQTT server if the connection is lost
void reconnect() {
    // Loop until reconnected
    while (!client.connected()) {
        Serial.print("Attempting MQTT connection...");
        // Create a random client ID
        String clientId = "ESP32Client-";
        clientId += String(WiFi.macAddress());

        // Attempt to connect
        if (client.connect(clientId.c_str(), SECRET_MQTTUSER, SECRET_MQTTPASS)) {
            Serial.println("connected");
            // Subscribe to the topic
            client.subscribe("student/ucbvren/headsets/headset2");
        } else {
            Serial.print("failed, rc=");
            Serial.print(client.state());
            Serial.println(" try again in 5 seconds");
            // Wait 5 seconds before retrying
            delay(5000);
        }
    }
}
