import csv
import matplotlib.pyplot as plt

# ── Settings ──────────────────────────────────────────────
INPUT_FILE = "data/paula/raw/mum_toast_01.csv"
# ──────────────────────────────────────────────────────────

def main():
    timestamps = []
    accX, accY, accZ = [], [], []
    gyroX, gyroY, gyroZ = [], [], []

    with open(INPUT_FILE, "r") as f:
        reader = csv.reader(f)
        next(reader)  # skip header
        for row in reader:
            try:
                timestamps.append(int(row[0]) / 1000)
                accX.append(float(row[1]))
                accY.append(float(row[2]))
                accZ.append(float(row[3]))
                gyroX.append(float(row[4]))
                gyroY.append(float(row[5]))
                gyroZ.append(float(row[6]))
            except (ValueError, IndexError):
                continue

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 8), sharex=True)
    fig.suptitle("Awareness Fork — Recording Overview", fontsize=14, fontweight="bold")

    # ── Top plot: all 3 acc axes ──────────────────────────
    ax1.plot(timestamps, accX, color="#0F6E56", linewidth=0.8, label="accX", alpha=0.8)
    ax1.plot(timestamps, accY, color="#854F0B", linewidth=0.8, label="accY", alpha=0.8)
    ax1.plot(timestamps, accZ, color="#185FA5", linewidth=0.8, label="accZ", alpha=0.9)
    ax1.axhline(y=1.0,  color="#185FA5", linewidth=0.5, linestyle="--", alpha=0.4)
    ax1.axhline(y=0.0,  color="gray",    linewidth=0.5, linestyle="--", alpha=0.3)
    ax1.axhline(y=-1.0, color="#854F0B", linewidth=0.5, linestyle="--", alpha=0.4)
    ax1.set_ylabel("Acceleration (g-force)")
    ax1.set_title("All 3 acceleration axes — changes during movement visible across axes")
    ax1.legend(loc="upper right", fontsize=9)
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim(-2.5, 3)

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

    print("Tips for reading the plot:")
    print("  accZ ≈ +1.0 at rest (gravity on Z axis) — may drop during movement")
    print("  accY typically shows strongest movement signal for bite movements")
    print("  accX ≈  0.0 at rest")
    print("")
    print("During a bite: watch which acc axis changes most!")
    print("Use zoom tool to identify individual movements for labeling.")
    print("X-axis = seconds → multiply by 1000 for label.py timestamps")

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()