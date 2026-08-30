import csv
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

# ── Settings ──────────────────────────────────────────────
INPUT_FILE = "data/paula/raw/mum_noodles_01.csv"
WINDOW_SEC = 30  # how many seconds visible at once
# ──────────────────────────────────────────────────────────

def main():
    timestamps_raw = []
    accX, accY, accZ = [], [], []
    gyroX, gyroY, gyroZ = [], [], []

    with open(INPUT_FILE, "r") as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            try:
                timestamps_raw.append(int(row[0]))
                accX.append(float(row[1]))
                accY.append(float(row[2]))
                accZ.append(float(row[3]))
                gyroX.append(float(row[4]))
                gyroY.append(float(row[5]))
                gyroZ.append(float(row[6]))
            except (ValueError, IndexError):
                continue

    # Make timestamps relative to start
    start = timestamps_raw[0]
    timestamps = [(t - start) / 1000 for t in timestamps_raw]
    total_duration = timestamps[-1]

    # Axis importance
    axes_std = {
        "accX":  np.std(accX),
        "accY":  np.std(accY),
        "accZ":  np.std(accZ),
        "gyroX": np.std(gyroX),
        "gyroY": np.std(gyroY),
        "gyroZ": np.std(gyroZ),
    }
    print("\n── Axis Importance (standard deviation) ──")
    for name, std in sorted(axes_std.items(), key=lambda x: -x[1]):
        bar = "█" * int(std * 2)
        print(f"  {name:6s}: {std:.3f}  {bar}")
    print(f"\n  → Recording duration: {total_duration:.1f} seconds")
    print(f"  → Total rows: {len(timestamps)}")
    print(f"\nHover over plot to see exact timestamp (x = seconds from start)")
    print(f"Multiply by 1000 for label.py\n")

    # ── Plot ─────────────────────────────────────────────
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 9))
    plt.subplots_adjust(bottom=0.15, hspace=0.35)
    fig.suptitle("Awareness Fork — Recording Overview (use slider to scroll)",
                 fontsize=13, fontweight="bold")

    # Plot all data
    l_accY, = ax1.plot(timestamps, accY, color="#854F0B", linewidth=0.8,
                        label=f"accY (std={axes_std['accY']:.3f})", alpha=0.9)
    l_accZ, = ax1.plot(timestamps, accZ, color="#185FA5", linewidth=0.8,
                        label=f"accZ (std={axes_std['accZ']:.3f})", alpha=0.9)
    ax1.axhline(y=1.0, color="gray", linewidth=0.5, linestyle="--", alpha=0.4)
    ax1.axhline(y=0.0, color="gray", linewidth=0.5, linestyle="--", alpha=0.3)
    ax1.set_ylabel("Acceleration (g-force)")
    ax1.set_title("accY + accZ (most informative acceleration axes)")
    ax1.legend(loc="upper right", fontsize=9)
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim(-2.5, 3)
    ax1.set_xlim(0, WINDOW_SEC)

    l_gX, = ax2.plot(timestamps, gyroX, color="#0F6E56", linewidth=0.6,
                      label=f"gyroX (std={axes_std['gyroX']:.3f})", alpha=0.8)
    l_gY, = ax2.plot(timestamps, gyroY, color="#854F0B", linewidth=0.6,
                      label=f"gyroY (std={axes_std['gyroY']:.3f})", alpha=0.8)
    l_gZ, = ax2.plot(timestamps, gyroZ, color="#185FA5", linewidth=0.6,
                      label=f"gyroZ (std={axes_std['gyroZ']:.3f})", alpha=0.8)
    ax2.axhline(y=0, color="gray", linewidth=0.5, linestyle="--", alpha=0.5)
    ax2.set_ylabel("Rotation (deg/sec)")
    ax2.set_xlabel("Time (seconds, relative to start of recording)")
    ax2.set_title("Gyroscope — all 3 axes")
    ax2.legend(loc="upper right", fontsize=9)
    ax2.grid(True, alpha=0.3)
    ax2.set_xlim(0, WINDOW_SEC)

    # ── Slider to scroll through recording ───────────────
    ax_slider = plt.axes([0.15, 0.04, 0.70, 0.03])
    slider = Slider(ax_slider, "Scroll (sec)", 0,
                    max(0, total_duration - WINDOW_SEC),
                    valinit=0, valstep=1)

    def update(val):
        pos = slider.val
        ax1.set_xlim(pos, pos + WINDOW_SEC)
        ax2.set_xlim(pos, pos + WINDOW_SEC)
        fig.canvas.draw_idle()

    slider.on_changed(update)

    plt.show()

if __name__ == "__main__":
    main()