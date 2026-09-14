import csv
import os

# ── Settings ──────────────────────────────────────────────
INPUT_FILE  = "data/paula/raw/sister_cake_01.csv"
OUTPUT_FILE = "data/paula/labeled/sister_cake_01_labeled.csv"

# ── Labels (start_sec, end_sec, label) ────────────────────
LABELS = [
    (20.24, 23.22, "other"),
    (23.22, 24.45, "bite"),
    (24.45, 30.81, "other"),
    (30.81, 32.64, "bite"),
    (32.64, 36.13, "other"),
    (36.13, 37.30, "bite"),
    (37.30, 39.10, "other"),
    (39.10, 40.38, "bite"),
    (40.38, 48.96, "other"),
    (48.96, 50.00, "bite"),
    (50.00, 51.90, "other"),
    (51.90, 53.55, "bite"),
    (53.55, 59.56, "other"),
    (59.56, 61.28, "bite"),
    (61.28, 64.43, "other"),
    (64.43, 67.17, "bite"),
    (67.17, 72.54, "other"),
    (72.54, 78.73, "bite"),   # long bite — paused to talk mid-bite
    (78.73, 89.04, "other"),
    (89.04, 96.29, "bite"),   # long bite — paused to talk mid-bite
    (96.29, 114.32, "other"),
    (114.32, 116.20, "bite"),
    (116.20, 130.53, "other"),
    (130.53, 133.82, "bite"),
    (133.82, 144.70, "other"),
    (144.70, 146.94, "bite"),
    (146.94, 999.0, "other"),
]
# ──────────────────────────────────────────────────────────

def get_label(timestamp_ms, start_ms):
    t_sec = (timestamp_ms - start_ms) / 1000
    for start, end, label in LABELS:
        if start <= t_sec < end:
            return label
    return "other"

def main():
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    total = 0
    label_counts = {}
    start_ms = None

    with open(INPUT_FILE, "r") as infile, \
         open(OUTPUT_FILE, "w", newline="") as outfile:

        reader = csv.reader(infile)
        writer = csv.writer(outfile)

        header = next(reader)
        writer.writerow(header + ["label"])

        for row in reader:
            if not row:
                continue
            try:
                timestamp_ms = int(row[0])
                if start_ms is None:
                    start_ms = timestamp_ms
                label = get_label(timestamp_ms, start_ms)
                writer.writerow(row + [label])
                total += 1
                label_counts[label] = label_counts.get(label, 0) + 1
            except (ValueError, IndexError):
                continue

    print(f"\nDone! {total} rows processed.")
    print(f"\nLabel distribution:")
    for label, count in sorted(label_counts.items()):
        pct = round(count / total * 100, 1)
        print(f"  {label:10s}: {count:5d} rows ({pct}%)")
    print(f"\nOutput saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()