import csv
import os

# ── Settings ──────────────────────────────────────────────
INPUT_FILE  = "data/paula/raw/mum_banana_02.csv"
OUTPUT_FILE = "data/paula/labeled/mum_banana_02_labeled.csv"

# ── Labels (start_sec, end_sec, label) ────────────────────
LABELS = [
    (18.32, 22.99, "other"),
    (22.99, 24.56, "bite"),
    (24.56, 35.58, "other"),
    (35.58, 37.41, "bite"),
    (37.41, 50.12, "other"),
    (50.12, 51.79, "bite"),
    (51.79, 64.27, "other"),
    (64.27, 65.62, "bite"),
    (65.62, 77.43, "other"),
    (77.43, 78.99, "bite"),
    (78.99, 89.09, "other"),
    (89.09, 90.56, "bite"),
    (90.56, 103.93, "other"),
    (103.93, 105.25, "bite"),
    (105.25, 118.88, "other"),
    (118.88, 120.09, "bite"),
    (120.09, 132.36, "other"),
    (132.36, 133.39, "bite"),
    (133.39, 148.70, "other"),
    (148.70, 149.62, "bite"),
    (149.62, 160.75, "other"),
    (160.75, 162.15, "bite"),
    (162.15, 999.0, "other")
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