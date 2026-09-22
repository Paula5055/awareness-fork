import matplotlib
matplotlib.use("TkAgg")  # force an interactive backend, before pyplot is imported

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

# ── Settings ──────────────────────────────────────────────
INPUT_FILE   = "data/paula/labeled/mum_banana_02_labeled.csv"
WINDOW_SEC   = 20   # how many seconds are visible at once

# ──────────────────────────────────────────────────────────

def main():
    print(f"Loading {INPUT_FILE} ...")
    df = pd.read_csv(INPUT_FILE)
    print(f"Loaded {len(df)} rows.")

    t = (df["timestamp_ms"] - df["timestamp_ms"].iloc[0]) / 1000.0
    bite_track = (df["label"] == "bite").astype(int)
    t_max = t.iloc[-1]

    fig, axes = plt.subplots(3, 1, figsize=(14, 9), sharex=True)
    plt.subplots_adjust(bottom=0.15, hspace=0.3)

    # ── Plot 1: acceleration (accY, accZ) ──────────────────
    axes[0].plot(t, df["accY"], color="#1B7A8A", linewidth=0.8,
                 label=f"accY (std: {df['accY'].std():.3f})")
    axes[0].plot(t, df["accZ"], color="#C04A3A", linewidth=0.8,
                 label=f"accZ (std: {df['accZ'].std():.3f})")
    axes[0].set_ylabel("acceleration")
    axes[0].set_title(INPUT_FILE)
    axes[0].legend(loc="upper right", fontsize=8)

    # ── Plot 2: gyroscope (gyroX, gyroY, gyroZ) ────────────
    axes[1].plot(t, df["gyroX"], color="#C07A20", linewidth=0.8,
                 label=f"gyroX (std: {df['gyroX'].std():.2f})")
    axes[1].plot(t, df["gyroY"], color="#5A3A7A", linewidth=0.8,
                 label=f"gyroY (std: {df['gyroY'].std():.2f})")
    axes[1].plot(t, df["gyroZ"], color="#3F8F5F", linewidth=0.8,
                 label=f"gyroZ (std: {df['gyroZ'].std():.2f})")
    axes[1].set_ylabel("gyroscope (\u00b0/s)")
    axes[1].legend(loc="upper right", fontsize=8)

    # ── Plot 3: labels (bite / other) ──────────────────────
    axes[2].step(t, bite_track, color="#7B1734", linewidth=1.2, where="post")
    axes[2].fill_between(t, bite_track, step="post", alpha=0.15, color="#7B1734")
    axes[2].set_ylabel("label")
    axes[2].set_yticks([0, 1])
    axes[2].set_yticklabels(["other", "bite"])
    axes[2].set_xlabel("time (s)")

    # ── Scroll slider (same idea as plot_recording.py) ─────
    window = min(WINDOW_SEC, t_max) if t_max > 0 else 1
    axes[0].set_xlim(0, window)

    slider_max = max(t_max - window, 0.01)
    slider_ax = plt.axes([0.15, 0.03, 0.7, 0.03])
    slider = Slider(slider_ax, "scroll", 0, slider_max, valinit=0, valstep=0.5)

    def update(val):
        start = slider.val
        axes[0].set_xlim(start, start + window)
        fig.canvas.draw_idle()

    slider.on_changed(update)

    print("Opening plot window...")
    plt.show()
    print("Plot window closed.")

if __name__ == "__main__":
    main()