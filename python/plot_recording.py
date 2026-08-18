import csv
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# ── Settings ──────────────────────────────────────────────
INPUT_FILE = "data/paula/raw/mum_toast_01.csv"
# ──────────────────────────────────────────────────────────

def main():
    timestamps = []
    accZ = []
    gyroX = []
    gyroY = []
    gyroZ = []

    with open(INPUT_FILE, "r") as f:
        reader = csv.reader(f)
        next(reader)  # skip header
        for row in reader:
            try:
                timestamps.append(int(row[0]) / 1000)  # convert ms to seconds
                accZ.append(float(row[3]))
                gyroX.append(float(row[4]))
                gyroY.append(float(row[5]))
                gyroZ.append(float(row[6]))
            except (ValueError, IndexError):
                continue

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 8), sharex=True)
    fig.suptitle("Awareness Fork — Recording Overview", fontsize=14, fontweight="bold")

    # ── Top plot: accZ ────────────────────────────────────
    ax1.plot(timestamps, accZ, color="#185FA5", linewidth=0.8, label="accZ")
    ax1.axhline(y=1.0, color="gray", linewidth=0.5, linestyle="--", alpha=0.5)
    ax1.set_ylabel("accZ (g-force)")
    ax1.set_title("Vertical acceleration (accZ) — rises when fork lifts toward mouth")
    ax1.legend(loc="upper right", fontsize=9)
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim(-2, 3)

    # ── Bottom plot: gyroscope ────────────────────────────
    ax2.plot(timestamps, gyroX, color="#0F6E56", linewidth=0.6, label="gyroX", alpha=0.8)
    ax2.plot(timestamps, gyroY, color="#854F0B", linewidth=0.6, label="gyroY", alpha=0.8)
    ax2.plot(timestamps, gyroZ, color="#185FA5", linewidth=0.6, label="gyroZ", alpha=0.8)
    ax2.axhline(y=0, color="gray", linewidth=0.5, linestyle="--", alpha=0.5)
    ax2.set_ylabel("Rotation (deg/sec)")
    ax2.set_xlabel("Time (seconds)")
    ax2.set_title("Gyroscope — spikes show rotation/tilting movements")
    ax2.legend(loc="upper right", fontsize=9)
    ax2.grid(True, alpha=0.3)

    # ── Instructions printed to terminal ─────────────────
    print("Plot is open! Use it to find your movement timestamps.")
    print("Zoom in with the magnifier tool in the plot window.")
    print("")
    print("What to look for:")
    print("  bite  → accZ rises above 1.3, gyro spikes")
    print("  cut   → small repetitive gyro movements")
    print("  scoop → accX/Y change, gyro shows rotation")
    print("  rest  → everything flat, accZ ≈ 1.0")
    print("")
    print("Note down the START and END timestamps (x-axis = seconds)")
    print("then fill them into label.py!")

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()