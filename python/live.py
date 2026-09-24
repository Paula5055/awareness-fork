"""
Awareness Fork — live.py
Reads sensor data from the ESP32 in real time, runs the trained GRU model
continuously, detects bite events, and triggers the vibration motor if
the gap between two bites is shorter than the science-based threshold
(18 sec, based on the 20:20:20 rule).

Tuned to a middle ground between the original defaults and the earlier
"safety version" (which favored catching every bite over avoiding false
alarms) — now that the final model is trained on all 12 recordings.
"""

import re
import time
from collections import deque

import numpy as np
import serial
import tensorflow as tf

# ── Settings ──────────────────────────────────────────────────────────
SERIAL_PORT   = "COM4"      # same port used in Arduino IDE / record.py — adjust if needed
BAUD_RATE     = 115200      # must match the baud rate set in the Arduino sketch

MODEL_FILE    = "model/awareness_fork_gru_final.keras"
NORM_FILE     = "model/awareness_fork_gru_final.norm.npz"

WINDOW_SIZE   = 100          # must match train.py (2 sec @ 50 Hz)
CONFIRM_STEPS = 5            # consecutive "bite" predictions needed to confirm a real bite start — middle ground between 6 (default) and 4 (safety version)
PRED_THRESHOLD = 0.42        # probability above which a timestep counts as "bite" — middle ground between 0.5 (default) and 0.35 (safety version)
BITE_THRESHOLD_SEC = 18.0    # gap between bites below this triggers vibration (20:20:20 rule, slightly relaxed)

VIBRATE_COMMAND = b"V"       # single byte sent to the ESP32 to trigger vibration

# ──────────────────────────────────────────────────────────────────────

LINE_PATTERN = re.compile(
    r"accX:\s*(-?\d+\.?\d*)\s*accY:\s*(-?\d+\.?\d*)\s*accZ:\s*(-?\d+\.?\d*)\s*\|\s*"
    r"gyroX:\s*(-?\d+\.?\d*)\s*gyroY:\s*(-?\d+\.?\d*)\s*gyroZ:\s*(-?\d+\.?\d*)"
)


def load_model_and_norm():
    print(f"Loading model from {MODEL_FILE} ...")
    model = tf.keras.models.load_model(MODEL_FILE)

    print(f"Loading normalization stats from {NORM_FILE} ...")
    norm = np.load(NORM_FILE, allow_pickle=True)
    mean, std, feature_cols = norm["mean"], norm["std"], list(norm["feature_cols"])
    print(f"Features used (in order): {feature_cols}")

    # Build ONE fixed, reusable computation graph for exactly our input shape
    # (1, WINDOW_SIZE, num_features). This is what makes repeated calls fast —
    # tf.function traces the model once, then reuses that compiled graph on
    # every later call, instead of re-executing the model layer-by-layer in
    # plain Python each time.
    num_features = len(feature_cols)

    @tf.function(input_signature=[tf.TensorSpec(shape=[1, WINDOW_SIZE, num_features], dtype=tf.float32)])
    def predict_fn(x):
        return model(x, training=False)

    # "warm up" — the FIRST call to a tf.function is what actually does the
    # slow tracing/compiling. Doing that once here means it happens before
    # you start eating, not during your first real bite.
    print("Warming up model (building the computation graph once)...")
    dummy_input = tf.zeros((1, WINDOW_SIZE, num_features), dtype=tf.float32)
    _ = predict_fn(dummy_input)
    print("Model ready.")

    return predict_fn, mean, std, feature_cols


def parse_line(line, feature_cols):
    """
    Parses one line of the Arduino sketch's raw output, e.g.:
    accX: 0.38 accY: -0.12 accZ: 0.96 | gyroX: -3.71 gyroY: -0.95 gyroZ: -0.24
    Returns a feature vector in the exact order feature_cols expects
    (including the engineered acc_diff feature), or None if the line
    doesn't match (e.g. a stray "Ready!" or "QMI8658 found!" message).
    """
    match = LINE_PATTERN.search(line)
    if not match:
        return None

    accX, accY, accZ, gyroX, gyroY, gyroZ = [float(v) for v in match.groups()]
    row = {
        "accX": accX, "accY": accY, "accZ": accZ,
        "gyroX": gyroX, "gyroY": gyroY, "gyroZ": gyroZ,
        "acc_diff": accY - accZ,
    }
    return [row[c] for c in feature_cols]


def main():
    predict_fn, mean, std, feature_cols = load_model_and_norm()

    print(f"Opening serial port {SERIAL_PORT} @ {BAUD_RATE} baud ...")
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)  # give the ESP32 a moment after the connection resets it
    ser.reset_input_buffer()

    buffer = deque(maxlen=WINDOW_SIZE)
    recent_raw_predictions = deque(maxlen=CONFIRM_STEPS)

    in_bite = False
    last_bite_time = None
    start_time = time.time()

    # ── Diagnostics: track how long predictions take ───────────────────
    slow_prediction_count = 0
    total_prediction_count = 0

    print("\nListening for sensor data. Press Ctrl+C to stop.\n")

    try:
        while True:
            line = ser.readline().decode("utf-8", errors="ignore")
            if not line:
                continue

            features = parse_line(line, feature_cols)
            if features is None:
                continue

            buffer.append(features)
            if len(buffer) < WINDOW_SIZE:
                continue  # not enough history yet to make a prediction

            # normalize using the SAME mean/std computed during training
            window = np.array(buffer, dtype=np.float32)
            window_norm = (window - mean) / std
            window_norm = tf.convert_to_tensor(window_norm[np.newaxis, ...], dtype=tf.float32)

            # ── Diagnostics: time the prediction itself ─────────────────
            t_predict_start = time.time()
            pred_prob = predict_fn(window_norm).numpy()
            t_predict_end = time.time()

            total_prediction_count += 1
            predict_ms = (t_predict_end - t_predict_start) * 1000
            if predict_ms > 20:  # longer than the 20ms gap between sensor readings
                slow_prediction_count += 1

            # we only care about the prediction for the most recent timestep
            raw_bite = pred_prob[0, -1, 0] >= PRED_THRESHOLD
            recent_raw_predictions.append(raw_bite)

            now = time.time() - start_time

            # confirmed bite START: was not in a bite, and the last
            # CONFIRM_STEPS predictions were all "bite"
            if (not in_bite
                    and len(recent_raw_predictions) == CONFIRM_STEPS
                    and all(recent_raw_predictions)):
                in_bite = True

                if last_bite_time is not None:
                    gap = now - last_bite_time
                    print(f"[{now:6.2f}s] Bite detected. Gap since last bite: {gap:.2f}s", end="")
                    if gap < BITE_THRESHOLD_SEC:
                        print("  -> TOO FAST, vibrating!")
                        ser.write(VIBRATE_COMMAND)
                    else:
                        print("  -> ok")
                else:
                    print(f"[{now:6.2f}s] First bite detected.")

                last_bite_time = now

            # bite END: prediction dropped back to "other"
            elif in_bite and not raw_bite:
                in_bite = False

    except KeyboardInterrupt:
        print("\nStopping...")
        if total_prediction_count > 0:
            pct_slow = 100 * slow_prediction_count / total_prediction_count
            print(f"\nDiagnostics: {slow_prediction_count}/{total_prediction_count} "
                  f"predictions were slower than real-time ({pct_slow:.1f}%)")
    finally:
        ser.close()
        print("Serial port closed.")


if __name__ == "__main__":
    main()