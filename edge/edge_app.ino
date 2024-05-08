#include <WiFi.h>
#include <WiFiClient.h>
#include <TaskScheduler.h>

void startWifiConnection();
void uploadData();
String formatHttpRequest(String body, String host);
String getNewData(String deviceId);

char* ssid = "YourWifiSSID";
char* password = "YourWifiPassword";
const char* host = "my-cloud-server.com"; // Cloud server host address
String deviceId = "AC"; // Device ID, assumes one device has one ESP

Task sender(600000, TASK_FOREVER, &uploadData);
Scheduler schedule;
WiFiClient client;

void setup() {
  Serial.begin(9600);
  // start connect to the WiFi AP
  startWifiConnection();
  // add task to send data to cloud to scheduler
  schedule.addTask(sender);
  sender.enable();
}

void loop() {
  // Execute the sender task if it is the time
  schedule.execute();
  // If somehow the WiFi disconnected, reconnect again
  if (WiFi.status() != WL_CONNECTED){
    startWifiConnection();
  }
}

void startWifiConnection(){
  /* This function handles the connection to the WiFi AP */

  WiFi.begin(ssid, password); // set AP SSID and password
  WiFi.mode(WIFI_STA); // connect to AP
  int i = 0;
  // try reconnect until connected
  while (WiFi.status() != WL_CONNECTED && i<50) {
    delay(500);
    Serial.print(".");
    i++;
  }
}

void uploadData(){
  /* This function handles the upload of the data to the cloud server */

  // Get new data iin JSON format
  String postData = getNewData(deviceId);
  // Only try sending when connected to WiFi
  if (WiFi.status() == WL_CONNECTED){ 
    // Try connect to cloud server
    if (client.connect( host , 80 )) { 
      String request = formatHttpRequest(postData, String(host)); // Create the HTTP request
      client.print(request); // Send the HTTP request
      // Wait until disconnected from host or get OK response
      while (client.connected()) {  
        String resp = client.readStringUntil('\n');
        int respCode = resp.indexOf("200 OK");
        if (respCode > 0 ) {
          break;
        }
      }    
    }
  }
}

String formatHttpRequest(String body, String host){
  /* This function handles creation of HTTP request to push new data */

  String request = "POST /update HTTP/1.1\r\n";
  request += "Host: " + host + "\r\n";
  request += "content-type: application/json\r\n";
  request += "Connection: close\r\n";
  request += "Content-Length: " + String(body.length()) + "\r\n\r\n";
  request += body;
}

String getNewData(String deviceId){
  /* Retrieve data and format as JSON */

  // Get current data from sensors
  int newVoltage = getCurrentVoltage(); // Unimplemented
  int newAmpere = getCurrentAmpere(); // Unimplemented
  int newTimestamp = getCurrentTimestamp(); // Unimplemented

  // Format data to JSON
  String postData = "{\"Device ID\":\"" + deviceId;
  postData += "\", \"Voltage (V)\":" + String(newVoltage);
  postData += ", \"Ampere (A)\":" + String(newAmpere);
  postData += ", \"Timestamp\":" + String(newTimestamp) + "}";
  return postData;
}
