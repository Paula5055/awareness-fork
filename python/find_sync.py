import csv

INPUT_FILE = "data/paula/raw/mum_sandwich_01.csv"
GYRO_THRESHOLD = 30.0  # raised from 10 to filter out startup noise
SKIP_SECONDS = 5       # skip first 5 seconds

data = []
with open(INPUT_FILE, "r") as f:
    reader = csv.reader(f)
    next(reader)
    for row in reader:
        try:
            data.append([int(row[0]), float(row[1]), float(row[2]),
                         float(row[3]), float(row[4]), float(row[5]), float(row[6])])
        except:
            continue

start_ts = data[0][0]
print(f"Duration: {(data[-1][0] - start_ts) / 1000:.1f} seconds")
print(f"Total rows: {len(data)}")
print(f"\nFirst 5 significant movements (gyro > {GYRO_THRESHOLD} deg/sec, after {SKIP_SECONDS}s):")

found = 0
for row in data:
    t = (row[0] - start_ts) / 1000
    if t < SKIP_SECONDS:
        continue
    gyro_max = max(abs(row[4]), abs(row[5]), abs(row[6]))
    if gyro_max > GYRO_THRESHOLD:
        print(f"  t={t:.2f}s | accZ={row[3]:.3f} | gyroX={row[4]:.1f} gyroY={row[5]:.1f} gyroZ={row[6]:.1f}")
        found += 1
        if found >= 5:
            break