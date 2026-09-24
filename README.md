# The Awareness Fork — AI-Powered Mindful Eating

A clip-on fork sensor that detects eating speed and gives a gentle vibration nudge when you're eating too fast. Built as an AI Minor project at Leuphana University Lüneburg, presented at the Minor AI Conference (25 September 2026).

## Author

Paula Heide — AI Minor Project, Leuphana University Lüneburg, 2026

Repository: [Paula5055/awareness-fork](https://github.com/Paula5055/awareness-fork)

## How it works

A sensor clipped to the fork streams motion data (accelerometer + gyroscope, 50 times/sec) to a laptop, where a self-segmenting GRU model predicts, for every single reading, whether a bite is happening right now. If two bites happen closer together than ~18 seconds, the laptop sends a signal back to the fork, triggering a gentle vibration.

## Repository structure

```
awareness-fork/
├── arduino_alt/                # earlier ESP32-C3 SuperMini attempt (kept for reference)
├── arduino_neu/
│   ├── raw_sensor_data_waveshare/   # streams sensor data, used for training recordings
│   └── live_detection/              # streams data + listens for the vibration trigger
├── data/
│   ├── paula/
│   │   ├── raw/                # raw sensor recordings (CSV)
│   │   └── labeled/            # labeled recordings (bite / other)
│   └── lars/                   # shared, unused by Lars
├── model/
│   ├── awareness_fork_gru_final.keras       # final trained model
│   └── awareness_fork_gru_final.norm.npz    # matching normalization stats
├── python/
│   ├── record.py            # captures sensor data from the fork to CSV
│   ├── plot_recording.py    # scrollable graph of one recording, for a quick check
│   ├── find_sync.py         # finds the first gyroscope spike (for video sync)
│   ├── label.py             # converts video timestamps into labeled CSV rows
│   ├── plot_labeled.py      # visualizes sensor data + labels together
│   ├── plot_predictions.py  # visualizes model predictions vs. true labels
│   ├── train.py             # trains the GRU model on all labeled recordings
│   ├── peek_norm.py         # small utility: prints a saved .norm.npz's mean/std/feature order
│   └── live.py               # real-time bite detection + vibration trigger
└── README.md
```

## The pipeline, step by step

1. **Record** — `record.py` saves live sensor data to a CSV while someone eats, with a phone filming from the side as a labeling reference.
2. **Check** — `plot_recording.py` gives a quick visual sanity check.
3. **Sync** — `find_sync.py` finds the first clear motion spike in the CSV, to line up the recording with the video.
4. **Label** — `label.py` converts manually noted video timestamps into a labeled CSV (bite / other).
5. **Train** — `train.py` combines all labeled recordings, builds overlapping 2-second windows, and trains a self-segmenting GRU model.
6. **Analyze** — `plot_labeled.py` and `plot_predictions.py` help inspect the data and the model's predictions. `peek_norm.py` is a small utility to double-check what a saved `.norm.npz` file actually contains.
7. **Run live** — `live.py` loads the trained model and runs it in real time on a live sensor stream, triggering the fork's vibration motor.

## Dataset

12 recordings, 3 participants (Mum, Sister, Paula), 145,742 rows, 199 labeled bite segments in total.

## Model

The final model (`model/awareness_fork_gru_final.keras`) is trained on 11 of the 12 recordings, with `mum_noodles_01` held out for evaluation:

- Bite recall: 80%
- Bite precision: 53%

Architecture: GRU(32) → Dropout → GRU(16) → TimeDistributed Dense(1, sigmoid), trained on 2-second windows (75% overlap) with class-weighted loss.

## Hardware

- **Board**: Waveshare ESP32-S3-LCD-1.3, with a built-in QMI8658 IMU (accelerometer + gyroscope), wired to GPIO 47 (SDA) / GPIO 48 (SCL)
- **Vibration motor**: connected via its pre-attached pin header, pressed directly onto the board's GND / 3V3 / IO1 pads — no soldering required

