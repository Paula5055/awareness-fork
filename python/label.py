import csv
import os

# ── Settings ──────────────────────────────────────────────
INPUT_FILE  = "data/paula/raw//ich_noodles-with-vegetable-and-chicken_01.csv"
OUTPUT_FILE = "data/paula/labeled/ich_noodles-with-vegetable-and-chicken_01_labeled.csv"

# ── Labels (start_sec, end_sec, label) ────────────────────
LABELS = [
    (3.72, 11.56, "other"),
    (11.56, 12.89, "bite"),
    (12.89, 19.56, "other"),
    (19.56, 21.35, "bite"),
    (21.35, 29.96, "other"),
    (29.96, 32.30, "bite"),
    (32.30, 49.67, "other"),
    (49.67, 51.59, "bite"),
    (51.59, 62.99, "other"),
    (62.99, 65.00, "bite"),
    (65.00, 85.78, "other"),
    (85.78, 87.73, "bite"),
    (87.73, 100.44, "other"),
    (100.44, 102.49, "bite"),
    (102.49, 112.00, "other"),
    (112.00, 113.97, "bite"),
    (113.97, 133.07, "other"),
    (133.07, 134.61, "bite"),
    (134.61, 148.02, "other"),
    (148.02, 150.51, "bite"),
    (150.51, 165.95, "other"),
    (165.95, 167.73, "bite"),
    (167.73, 174.95, "other"),
    (174.95, 176.78, "bite"),
    (176.78, 180.80, "other"),
    (180.80, 182.55, "bite"),
    (182.55, 189.98, "other"),
    (189.98, 192.51, "bite"),
    (192.51, 217.08, "other"),
    (217.08, 219.91, "bite"),
    (219.91, 229.51, "other"),
    (229.51, 231.25, "bite"),
    (231.25, 240.89, "other"),
    (240.89, 242.13, "bite"),
    (242.13, 999.0, "other"),
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