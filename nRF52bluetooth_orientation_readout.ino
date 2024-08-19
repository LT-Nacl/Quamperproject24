#include <ArduinoBLE.h>
#include "LSM6DS3.h"
#include "Wire.h"

BLEService myService("12345678-1234-5678-1234-56789abcdef0"); // Custom BLE Service UUID
BLEStringCharacteristic myCharacteristic("12345678-1234-5678-1234-56789abcdef1", BLERead | BLEWrite, 100);



String message = "Init!"; 


//IMU setup
LSM6DS3 myIMU(I2C_MODE, 0x6A);
const float RAD_TO_DEG = 180.0 / M_PI;
float gx, gy, gz;
unsigned long lastTime;
float pitch = 0, roll = 0, yaw = 0;


void setup() {
  Serial.begin(9600);
  while (!Serial);

  checks
  if (!BLE.begin()) {
    Serial.println("Starting BLE failed!");
    while (1);
  }
  if (myIMU.begin() != 0) {
    Serial.println("Device error");
  }else {
      Serial.println("Device OK!");
    }

  //names [MUST BE UNIQUE!]
  BLE.setLocalName("NRF1");
  BLE.setAdvertisedService(myService);

  // Add the characteristic to the service
  myService.addCharacteristic(myCharacteristic);

  // Add the service
  BLE.addService(myService);

  // Set the initial value for the characteristic
  myCharacteristic.setValue(message);

  // Start advertising
  BLE.advertise();

  Serial.println("Advertising...");
}

void loop() {
  //bits and bobs for imu
  gx = myIMU.readFloatGyroX();
  gy = myIMU.readFloatGyroY();
  gz = myIMU.readFloatGyroZ();

  unsigned long currentTime = millis();
  float dt = (currentTime - lastTime) / 1000.0; 
  lastTime = currentTime;

  pitch += gx * dt;
  roll += gy * dt;
  yaw += gz * dt;

  float pitch_deg = pitch;
  float roll_deg = roll;
  float yaw_deg = yaw;

  pitch_deg = fmod(pitch_deg, 360.0);
  roll_deg = fmod(roll_deg, 360.0);
  yaw_deg = fmod(yaw_deg, 360.0);

  static unsigned long lastUpdate = 0;
  unsigned long currentMillis = millis();


  message = String(pitch_deg) + ',' + String(roll_deg) + ',' + String(yaw_deg);
  if (currentMillis - lastUpdate >= 200) {
    lastUpdate = currentMillis;
    myCharacteristic.setValue(message);
    Serial.println("Updated message: " + message + BLE.address());
  }

  BLE.poll(); // Process BLE events
}


