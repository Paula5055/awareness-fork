import serial
import csv
import time
import os

# ── Settings ──────────────────────────────────────────────
PORT = "COM4"
BAUD = 115200
OUTPUT_FILE = "data/paula/raw/meal_01.csv"
# ──────────────────────────────────────────────────────────

def main():
    print(f"Connecting to {PORT}...")
    ser = serial.Serial(PORT, BAUD, timeout=2)
    time.sleep(2)
    print("Connected! Press Ctrl+C to stop recording.")
    print(f"Saving to: {OUTPUT_FILE}")

    # Create folder if it doesn't exist
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    with open(OUTPUT_FILE, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)

        # Write header
        writer.writerow(["timestamp_ms", "accX", "accY", "accZ",
                          "gyroX", "gyroY", "gyroZ"])

        try:
            # Skip first few lines (startup messages from ESP32)
            for _ in range(5):
                ser.readline()

            while True:
                line = ser.readline().decode("utf-8").strip()
                if not line:
                    continue

                # Skip any non-data lines
                if not line[0].isdigit():
                    continue

                try:
                    parts = line.split(",")
                    if len(parts) != 7:
                        continue

                    timestamp_ms = int(parts[0])
                    accX  = float(parts[1])
                    accY  = float(parts[2])
                    accZ  = float(parts[3])
                    gyroX = float(parts[4])
                    gyroY = float(parts[5])
                    gyroZ = float(parts[6])

                    writer.writerow([timestamp_ms, accX, accY, accZ,
                                     gyroX, gyroY, gyroZ])
                    print(f"{timestamp_ms}ms | accZ: {accZ:.2f}")

                except (IndexError, ValueError):
                    continue

        except KeyboardInterrupt:
            print("\nRecording stopped!")
            print(f"File saved: {OUTPUT_FILE}")

    ser.close()

if __name__ == "__main__":
    main()