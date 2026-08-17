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
  Serial.println("Ready! Move the board!");
}

void loop() {
  if (qmi.getDataReady()) {
    qmi.getAccelerometer(acc.x, acc.y, acc.z);
    qmi.getGyroscope(gyr.x, gyr.y, gyr.z);

    Serial.print("accX: "); Serial.print(acc.x);
    Serial.print(" accY: "); Serial.print(acc.y);
    Serial.print(" accZ: "); Serial.print(acc.z);
    Serial.print(" | gyroX: "); Serial.print(gyr.x);
    Serial.print(" gyroY: "); Serial.print(gyr.y);
    Serial.print(" gyroZ: "); Serial.println(gyr.z);
  }
  delay(20);
}