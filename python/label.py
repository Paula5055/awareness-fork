import csv
import os

# ── Settings ──────────────────────────────────────────────
INPUT_FILE  = "data/paula/raw/sister_cake_02.csv"
OUTPUT_FILE = "data/paula/labeled/sister_cake_02_labeled.csv"

# ── Labels (start_sec, end_sec, label) ────────────────────
LABELS = [
    (17.62, 31.98, "other"),
    (31.98, 33.10, "bite"),
    (33.10, 46.85, "other"),
    (46.85, 48.87, "bite"),
    (48.87, 57.13, "other"),
    (57.13, 59.53, "bite"),
    (59.53, 75.51, "other"),
    (75.51, 77.13, "bite"),
    (77.13, 91.69, "other"),
    (91.69, 94.73, "bite"),
    (94.73, 108.54, "other"),
    (108.54, 110.76, "bite"),
    (110.76, 130.97, "other"),
    (130.97, 132.70, "bite"),
    (132.70, 145.67, "other"),
    (145.67, 147.40, "bite"),
    (147.40, 161.64, "other"),
    (161.64, 163.05, "bite"),
    (163.05, 177.36, "other"),
    (177.36, 179.99, "bite"),
    (179.99, 195.43, "other"),
    (195.43, 197.45, "bite"),
    (197.45, 212.97, "other"),
    (212.97, 215.46, "bite"),
    (215.46, 225.26, "other"),
    (225.26, 228.84, "bite"),
    (228.84, 244.39, "other"),
    (244.39, 245.85, "bite"),
    (245.85, 259.80, "other"),
    (259.80, 260.92, "bite"),
    (260.92, 999.0, "other")
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