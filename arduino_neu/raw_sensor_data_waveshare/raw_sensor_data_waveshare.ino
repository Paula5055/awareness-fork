#include <Wire.h>
#include <SensorQMI8658.hpp>

SensorQMI8658 qmi;
IMUdata acc;
IMUdata gyr;

void setup() {
  Serial.begin(115200);
  delay(1000);

  if (!qmi.begin(Wire, QMI8658_L_SLAVE_ADDRESS, 47, 48)) {
    Serial.println("QMI8658 not found!");
    while (1) delay(1000);
  }

  Serial.println("QMI8658 found!");
  qmi.configAccelerometer(SensorQMI8658::ACC_RANGE_4G,
                           SensorQMI8658::ACC_ODR_LOWPOWER_128Hz);
  qmi.configGyroscope(SensorQMI8658::GYR_RANGE_64DPS,
                       SensorQMI8658::GYR_ODR_112_1Hz);
  qmi.enableGyroscope();
  qmi.enableAccelerometer();

  // Print CSV header
  Serial.println("timestamp_ms,accX,accY,accZ,gyroX,gyroY,gyroZ");
}

void loop() {
  if (qmi.getDataReady()) {
    qmi.getAccelerometer(acc.x, acc.y, acc.z);
    qmi.getGyroscope(gyr.x, gyr.y, gyr.z);

    // ESP32 internal clock in milliseconds
    unsigned long timestamp_ms = millis();

    Serial.print(timestamp_ms);
    Serial.print(",");
    Serial.print(acc.x, 4);
    Serial.print(",");
    Serial.print(acc.y, 4);
    Serial.print(",");
    Serial.print(acc.z, 4);
    Serial.print(",");
    Serial.print(gyr.x, 4);
    Serial.print(",");
    Serial.print(gyr.y, 4);
    Serial.print(",");
    Serial.println(gyr.z, 4);
  }
  delay(20);
}
