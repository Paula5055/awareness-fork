import matplotlib
matplotlib.use("TkAgg")  # force an interactive backend, before pyplot is imported

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import tensorflow as tf

# ── Settings ──────────────────────────────────────────────
LABELED_FILE = "data/paula/labeled/mum_noodles_01_labeled.csv"
MODEL_FILE   = "model/awareness_fork_gru_test.keras"
NORM_FILE    = "model/awareness_fork_gru_test.norm.npz"
WINDOW_SIZE  = 100  # must match train.py
WINDOW_SEC   = 20   # how many seconds are visible at once in the plot

# ──────────────────────────────────────────────────────────

def main():
    print(f"Loading {LABELED_FILE} ...")
    df = pd.read_csv(LABELED_FILE)
    print(f"Loaded {len(df)} rows.")
    df["acc_diff"] = df["accY"] - df["accZ"]

    print(f"Loading normalization stats from {NORM_FILE} ...")
    norm = np.load(NORM_FILE, allow_pickle=True)
    mean, std, feature_cols = norm["mean"], norm["std"], list(norm["feature_cols"])

    values = df[feature_cols].values.astype(np.float32)
    true_bite = (df["label"] == "bite").astype(int).values
    t = (df["timestamp_ms"] - df["timestamp_ms"].iloc[0]) / 1000.0

    print(f"Loading model from {MODEL_FILE} ...")
    model = tf.keras.models.load_model(MODEL_FILE)

    # chop into consecutive (non-overlapping) windows, predict each, then
    # stitch the predictions back together into one continuous timeline
    n_windows = len(values) // WINDOW_SIZE
    usable_rows = n_windows * WINDOW_SIZE
    print(f"Running predictions on {n_windows} windows ({usable_rows} rows)...")

    windows = values[:usable_rows].reshape(n_windows, WINDOW_SIZE, -1)
    windows_norm = (windows - mean) / std

    pred_prob = model.predict(windows_norm, verbose=0)
    pred_bite = (pred_prob >= 0.5).astype(int).reshape(-1)

    t_used = t[:usable_rows].values
    true_used = true_bite[:usable_rows]
    accY_used = df["accY"].values[:usable_rows]
    accZ_used = df["accZ"].values[:usable_rows]
    gyroX_used = df["gyroX"].values[:usable_rows]
    gyroY_used = df["gyroY"].values[:usable_rows]
    gyroZ_used = df["gyroZ"].values[:usable_rows]

    mismatch = true_used != pred_bite
    acc = 1 - mismatch.mean()
    t_max = t_used[-1]

    fig, axes = plt.subplots(4, 1, figsize=(14, 11), sharex=True)
    plt.subplots_adjust(bottom=0.13, hspace=0.35)

    # ── Plot 1: acceleration ────────────────────────────────
    axes[0].plot(t_used, accY_used, color="#1B7A8A", linewidth=0.8, label="accY")
    axes[0].plot(t_used, accZ_used, color="#C04A3A", linewidth=0.8, label="accZ")
    axes[0].set_ylabel("acceleration")
    axes[0].set_title(f"{LABELED_FILE}\naccuracy on this recording: {acc*100:.1f}%")
    axes[0].legend(loc="upper right", fontsize=8)

    # ── Plot 2: gyroscope ───────────────────────────────────
    axes[1].plot(t_used, gyroX_used, color="#C07A20", linewidth=0.8, label="gyroX")
    axes[1].plot(t_used, gyroY_used, color="#5A3A7A", linewidth=0.8, label="gyroY")
    axes[1].plot(t_used, gyroZ_used, color="#3F8F5F", linewidth=0.8, label="gyroZ")
    axes[1].set_ylabel("gyroscope (\u00b0/s)")
    axes[1].legend(loc="upper right", fontsize=8)

    # ── Plot 3: true labels ─────────────────────────────────
    axes[2].step(t_used, true_used, color="#3F8F5F", linewidth=1.2, where="post")
    axes[2].fill_between(t_used, true_used, step="post", alpha=0.15, color="#3F8F5F")
    axes[2].set_ylabel("true label")
    axes[2].set_yticks([0, 1])
    axes[2].set_yticklabels(["other", "bite"])

    # ── Plot 4: predicted labels, mismatches highlighted ────
    axes[3].step(t_used, pred_bite, color="#5A3A7A", linewidth=1.2, where="post")
    axes[3].fill_between(t_used, pred_bite, step="post", alpha=0.15, color="#5A3A7A")
    axes[3].fill_between(t_used, 0, 1, where=mismatch, color="red", alpha=0.15,
                          step="post", label="mismatch")
    axes[3].set_ylabel("predicted")
    axes[3].set_yticks([0, 1])
    axes[3].set_yticklabels(["other", "bite"])
    axes[3].set_xlabel("time (s)")
    axes[3].legend(loc="upper right", fontsize=8)

    # ── Scroll slider (same idea as plot_recording.py) ─────
    window = min(WINDOW_SEC, t_max) if t_max > 0 else 1
    axes[0].set_xlim(0, window)

    slider_max = max(t_max - window, 0.01)
    slider_ax = plt.axes([0.15, 0.02, 0.7, 0.03])
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