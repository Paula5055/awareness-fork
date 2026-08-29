import csv

INPUT_FILE = "data/paula/raw/mum_rice_01.csv"
GYRO_THRESHOLD = 10.0

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
print("\nFirst 5 significant movements (gyro > 10 deg/sec):")

found = 0
for row in data:
    gyro_max = max(abs(row[4]), abs(row[5]), abs(row[6]))
    if gyro_max > GYRO_THRESHOLD:
        t = (row[0] - start_ts) / 1000
        print(f"  t={t:.2f}s | accZ={row[3]:.3f} | gyroX={row[4]:.1f} gyroY={row[5]:.1f} gyroZ={row[6]:.1f}")
        found += 1
        if found >= 5:
            break