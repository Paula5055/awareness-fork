"""
Awareness Fork — train.py
Trains a self-segmenting GRU on all labeled datasets.
Splits by WHOLE RECORDING (not by window) to avoid data leakage from
overlapping windows — this design holds whether you have 4 recordings or 40.
"""

import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.model_selection import GroupShuffleSplit
from sklearn.metrics import classification_report, confusion_matrix
import tensorflow as tf
from tensorflow.keras import layers, models, callbacks

# ── Settings ──────────────────────────────────────────────────────────
LABELED_DIR   = Path("data/paula/labeled")
WINDOW_SEC    = 2.0
SAMPLE_RATE   = 50
WINDOW_SIZE   = int(WINDOW_SEC * SAMPLE_RATE)   # 100 timesteps
STRIDE        = WINDOW_SIZE // 4                # 75% overlap
VAL_SPLIT     = 0.2
RANDOM_SEED   = 42
MODEL_OUT     = Path("model/awareness_fork_gru_test.keras")

# Set this to force specific recording(s) as validation, for fair
# before/after comparisons across runs. Leave as None for a random
# group split (GroupShuffleSplit).
VALIDATION_RECORDINGS = ["mum_noodles_01_labeled"]


# ── Step 1: Load & combine all labeled recordings ────────────────────
def load_all_recordings():
    csv_files = sorted(LABELED_DIR.glob("*_labeled.csv"))
    if not csv_files:
        raise FileNotFoundError(f"No labeled CSVs found in {LABELED_DIR}")

    recordings = []
    for f in csv_files:
        df = pd.read_csv(f)

        # engineered feature: acc axes diverge during a bite (tilt + motion
        # combined) — see project notes for the physical explanation
        df["acc_diff"] = df["accY"] - df["accZ"]

        feature_cols = [c for c in df.columns if c not in ("timestamp_ms", "label")]
        df["label_bin"] = (df["label"] == "bite").astype(np.float32)
        recordings.append({"name": f.stem, "df": df, "feature_cols": feature_cols})
        print(f"Loaded {f.name}: {len(df)} rows, "
              f"{df['label_bin'].mean()*100:.1f}% bite")
    return recordings


# ── Step 2: Cut each recording into overlapping windows ──────────────
# Also tracks which recording each window came from (the "group"),
# so we can split by whole recording instead of by window.
def make_windows(recordings):
    X_list, y_list, group_list = [], [], []
    feature_cols = recordings[0]["feature_cols"]

    for rec in recordings:
        df = rec["df"]
        values = df[feature_cols].values.astype(np.float32)
        labels = df["label_bin"].values.astype(np.float32)

        n_rows = len(df)
        for start in range(0, n_rows - WINDOW_SIZE + 1, STRIDE):
            end = start + WINDOW_SIZE
            X_list.append(values[start:end])
            y_list.append(labels[start:end])
            group_list.append(rec["name"])

    X = np.stack(X_list)
    y = np.stack(y_list)[..., np.newaxis]
    groups = np.array(group_list)
    return X, y, groups, feature_cols


# ── Step 3: Normalize sensor values ──────────────────────────────────
def normalize(X_train, X_val):
    mean = X_train.reshape(-1, X_train.shape[-1]).mean(axis=0)
    std  = X_train.reshape(-1, X_train.shape[-1]).std(axis=0) + 1e-8
    return (X_train - mean) / std, (X_val - mean) / std, mean, std


# ── Step 4: Build the self-segmenting GRU ────────────────────────────
def build_model(num_features):
    model = models.Sequential([
        layers.Input(shape=(WINDOW_SIZE, num_features)),
        layers.GRU(32, return_sequences=True),
        layers.Dropout(0.2),
        layers.GRU(16, return_sequences=True),
        layers.TimeDistributed(layers.Dense(1, activation="sigmoid")),
    ])
    model.compile(
        optimizer="adam",
        loss="binary_crossentropy",
        weighted_metrics=["accuracy"],
    )
    return model


# ── Step 5: Class-weighted sample weights (bite is rare!) ────────────
def make_sample_weights(y):
    y_flat = y.flatten()
    n_total = len(y_flat)
    n_bite  = y_flat.sum()
    n_other = n_total - n_bite

    w_bite  = n_total / (2 * n_bite)
    w_other = n_total / (2 * n_other)
    print(f"Class weights -> bite: {w_bite:.2f}, other: {w_other:.2f}")

    return np.where(y[..., 0] == 1, w_bite, w_other).astype(np.float32)


# ── Step 6: Evaluate on held-out validation windows ───────────────────
def evaluate(model, X_val, y_val):
    y_pred_prob = model.predict(X_val, verbose=0)
    y_pred = (y_pred_prob >= 0.5).astype(int).flatten()
    y_true = y_val.astype(int).flatten()

    print("\n" + "=" * 50)
    print("EVALUATION ON VALIDATION SET (held-out recordings)")
    print("=" * 50)
    print(classification_report(y_true, y_pred, target_names=["other", "bite"]))

    cm = confusion_matrix(y_true, y_pred)
    print("Confusion matrix (rows=true, cols=predicted):")
    print(f"                predicted_other  predicted_bite")
    print(f"true_other      {cm[0][0]:>15d}  {cm[0][1]:>14d}")
    print(f"true_bite       {cm[1][0]:>15d}  {cm[1][1]:>14d}")


# ── Main ──────────────────────────────────────────────────────────────
def main():
    print("Loading recordings...")
    recordings = load_all_recordings()

    print("\nCreating windows...")
    X, y, groups, feature_cols = make_windows(recordings)
    print(f"Total windows: {X.shape[0]} | window shape: {X.shape[1:]}")
    print(f"Features used: {feature_cols}")

    print("\nSplitting by WHOLE RECORDING (no leakage)...")
    if VALIDATION_RECORDINGS:
        val_mask = np.isin(groups, VALIDATION_RECORDINGS)
        train_idx = np.where(~val_mask)[0]
        val_idx = np.where(val_mask)[0]
        if len(val_idx) == 0:
            raise ValueError(
                f"No windows matched VALIDATION_RECORDINGS={VALIDATION_RECORDINGS}. "
                f"Available recordings: {sorted(set(groups))}"
            )
    else:
        gss = GroupShuffleSplit(n_splits=1, test_size=VAL_SPLIT, random_state=RANDOM_SEED)
        train_idx, val_idx = next(gss.split(X, y, groups=groups))

    X_train, X_val = X[train_idx], X[val_idx]
    y_train, y_val = y[train_idx], y[val_idx]

    print(f"Train windows: {len(X_train)} (from {sorted(set(groups[train_idx]))})")
    print(f"Validation windows: {len(X_val)} (from {sorted(set(groups[val_idx]))})")

    print("\nNormalizing...")
    X_train, X_val, mean, std = normalize(X_train, X_val)

    print("\nBuilding model...")
    model = build_model(num_features=len(feature_cols))
    model.summary()

    print("\nComputing sample weights...")
    sample_weight = make_sample_weights(y_train)

    print("\nTraining...")
    early_stop = callbacks.EarlyStopping(
        monitor="val_loss", patience=5, restore_best_weights=True
    )
    model.fit(
        X_train, y_train,
        sample_weight=sample_weight,
        validation_data=(X_val, y_val),
        epochs=30,
        batch_size=32,
        callbacks=[early_stop],
        verbose=1,
    )

    evaluate(model, X_val, y_val)

    MODEL_OUT.parent.mkdir(exist_ok=True)
    model.save(MODEL_OUT)
    np.savez(MODEL_OUT.with_suffix(".norm.npz"), mean=mean, std=std, feature_cols=feature_cols)
    print(f"\nModel saved to {MODEL_OUT}")
    print(f"Normalization stats saved to {MODEL_OUT.with_suffix('.norm.npz')}")


if __name__ == "__main__":
    main()