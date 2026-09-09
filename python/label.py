import csv
import os

# ── Settings ──────────────────────────────────────────────
INPUT_FILE  = "data/paula/raw/mum_breadegg_01.csv"
OUTPUT_FILE = "data/paula/labeled/mum_breadegg_01_labeled.csv"

# ── Labels (start_sec, end_sec, label) ────────────────────
LABELS = [
    (21.46, 29.14, "other"),
    (29.14, 30.74, "bite"),
    (30.74, 45.65, "other"),
    (45.65, 47.20, "bite"),
    (47.20, 63.49, "other"),
    (63.49, 65.46, "bite"),
    (65.46, 80.62, "other"),
    (80.62, 82.79, "bite"),
    (82.79, 98.23, "other"),
    (98.23, 99.65, "bite"),
    (99.65, 118.16, "other"),
    (118.16, 119.57, "bite"),
    (119.57, 137.43, "other"),
    (137.43, 139.77, "bite"),
    (139.77, 160.18, "other"),
    (160.18, 162.02, "bite"),
    (162.02, 180.42, "other"),
    (180.42, 182.23, "bite"),
    (182.23, 210.58, "other"),
    (210.58, 212.50, "bite"),
    (212.50, 227.60, "other"),
    (227.60, 229.19, "bite"),
    (229.19, 241.17, "other"),
    (241.17, 243.03, "bite"),
    (243.03, 255.62, "other"),
    (255.62, 257.98, "bite"),
    (257.98, 282.71, "other"),
    (282.71, 284.29, "bite"),
    (284.29, 298.26, "other"),
    (298.26, 300.10, "bite"),
    (300.10, 323.33, "other"),
    (323.33, 324.69, "bite"),
    (324.69, 337.33, "other"),
    (337.33, 338.85, "bite"),
    (338.85, 353.17, "other"),
    (353.17, 354.53, "bite"),
    (354.53, 377.03, "other"),
    (377.03, 378.79, "bite"),
    (378.79, 402.90, "other"),
    (402.90, 404.63, "bite"),
    (404.63, 428.21, "other"),
    (428.21, 429.75, "bite"),
    (429.75, 447.33, "other"),
    (447.33, 449.02, "bite"),
    (449.02, 999.0, "other")
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