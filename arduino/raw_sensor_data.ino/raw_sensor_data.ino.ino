#include <Wire.h>

const int MPU_ADDR = 0x68; // I2C address we found earlier

int16_t accX, accY, accZ;
int16_t gyroX, gyroY, gyroZ;

void setup() {
  Serial.begin(115200);
  Wire.begin(21, 22);

  // Wake up the MPU-6050 (it starts in sleep mode by default)
  Wire.beginTransmission(MPU_ADDR);
  Wire.write(0x6B); // power management register
  Wire.write(0);    // set to 0 = wake up
  Wire.endTransmission(true);

  Serial.println("MPU-6050 ready. Move the sensor!");
}

void loop() {
  Wire.beginTransmission(MPU_ADDR);
  Wire.write(0x3B); // starting register for accelerometer data
  Wire.endTransmission(false);
  Wire.requestFrom(MPU_ADDR, 14, true); // request 14 bytes

  accX = Wire.read() << 8 | Wire.read();
  accY = Wire.read() << 8 | Wire.read();
  accZ = Wire.read() << 8 | Wire.read();
  Wire.read(); Wire.read(); // skip temperature bytes
  gyroX = Wire.read() << 8 | Wire.read();
  gyroY = Wire.read() << 8 | Wire.read();
  gyroZ = Wire.read() << 8 | Wire.read();

  // Convert to readable units (roughly g-force and degrees/sec)
  Serial.print("accX: "); Serial.print(accX / 16384.0);
  Serial.print(" accY: "); Serial.print(accY / 16384.0);
  Serial.print(" accZ: "); Serial.print(accZ / 16384.0);
  Serial.print(" | gyroX: "); Serial.print(gyroX / 131.0);
  Serial.print(" gyroY: "); Serial.print(gyroY / 131.0);
  Serial.print(" gyroZ: "); Serial.println(gyroZ / 131.0);

  delay(1000); // print 10 times per second (slow enough to read)
}