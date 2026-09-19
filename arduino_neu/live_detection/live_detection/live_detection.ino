#include <Wire.h>
#include <SensorQMI8658.hpp>

SensorQMI8658 qmi;
IMUdata acc;
IMUdata gyr;

#define MOTOR_PIN 1  // IO1
#define VIBRATE_DURATION_MS 400

bool vibrating = false;
unsigned long vibrateStartTime = 0;

void setup() {
  Serial.begin(115200);
  delay(1000);

  pinMode(MOTOR_PIN, OUTPUT);
  digitalWrite(MOTOR_PIN, LOW);

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
  // ── Check for a vibration command from live.py (non-blocking) ────────
  if (Serial.available() > 0) {
    char command = Serial.read();
    if (command == 'V' && !vibrating) {
      digitalWrite(MOTOR_PIN, HIGH);
      vibrating = true;
      vibrateStartTime = millis();
    }
  }

  // ── Turn the motor back off once VIBRATE_DURATION_MS has passed ──────
  if (vibrating && (millis() - vibrateStartTime >= VIBRATE_DURATION_MS)) {
    digitalWrite(MOTOR_PIN, LOW);
    vibrating = false;
  }

  // ── Stream sensor data, exactly as before ─────────────────────────────
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