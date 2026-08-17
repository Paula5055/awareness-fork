import serial
import csv
import time
import os

# ── Settings ──────────────────────────────────────────────
PORT = "COM4"        # your ESP32 port
BAUD = 115200
OUTPUT_FILE = "data/paula/raw/meal_01.csv" # ──────────────────────────────────────────────────────────

def main():
    print(f"Connecting to {PORT}...")
    ser = serial.Serial(PORT, BAUD, timeout=2)
    time.sleep(2)  # wait for ESP32 to reset
    print("Connected! Press Ctrl+C to stop recording.")
    print(f"Saving to: {OUTPUT_FILE}")

    # Create folder if it doesn't exist
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    with open(OUTPUT_FILE, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        # Write header row
        writer.writerow(["timestamp", "accX", "accY", "accZ",
                          "gyroX", "gyroY", "gyroZ"])

        start_time = time.time()

        try:
            while True:
                line = ser.readline().decode("utf-8").strip()
                if not line:
                    continue

                # Parse the line from ESP32
                # Expected format: "accX: 0.96 accY: 0.08 accZ: 1.05 | gyroX: -3.51 gyroY: -1.54 gyroZ: -0.37"
                try:
                    parts = line.replace("|", "").split()
                    accX  = float(parts[1])
                    accY  = float(parts[3])
                    accZ  = float(parts[5])
                    gyroX = float(parts[7])
                    gyroY = float(parts[9])
                    gyroZ = float(parts[11])

                    timestamp = round(time.time() - start_time, 3)
                    writer.writerow([timestamp, accX, accY, accZ,
                                     gyroX, gyroY, gyroZ])
                    print(f"{timestamp:.2f}s | accZ: {accZ:.2f}")

                except (IndexError, ValueError):
                    # Skip any malformed lines
                    continue

        except KeyboardInterrupt:
            print("\nRecording stopped!")
            print(f"File saved: {OUTPUT_FILE}")

    ser.close()

if __name__ == "__main__":
    main()