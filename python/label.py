import csv
import os

# ── Settings ──────────────────────────────────────────────
INPUT_FILE  = "data/paula/raw/mum_noodles_01.csv"
OUTPUT_FILE = "data/paula/labeled/mum_noodles_01_labeled.csv"

# ── Labels (start_sec, end_sec, label) ────────────────────
LABELS = [
    (5.01, 7.01, "other"),
    (7.01, 16.01, "other"),
    (16.01, 18.01, "bite"),
    (18.01, 29.01, "other"),
    (29.01, 31.01, "bite"),
    (31.01, 41.01, "other"),
    (41.01, 43.01, "bite"),
    (43.01, 53.01, "other"),
    (53.01, 55.01, "bite"),
    (55.01, 69.01, "other"),
    (69.01, 71.01, "bite"),
    (71.01, 87.01, "other"),
    (87.01, 89.01, "bite"),
    (89.01, 105.01, "other"),
    (105.01, 107.01, "bite"),
    (107.01, 117.01, "other"),
    (117.01, 119.01, "bite"),
    (119.01, 134.01, "other"),
    (134.01, 136.01, "bite"),
    (136.01, 156.01, "other"),
    (156.01, 159.01, "bite"),
    (159.01, 174.01, "other"),
    (174.01, 176.01, "bite"),
    (176.01, 187.01, "other"),
    (187.01, 189.01, "bite"),
    (189.01, 201.01, "other"),
    (201.01, 203.01, "bite"),
    (203.01, 223.01, "other"),
    (223.01, 226.01, "bite"),
    (226.01, 240.01, "other"),
    (240.01, 242.01, "bite"),
    (242.01, 259.01, "other"),
    (259.01, 262.01, "bite"),
    (262.01, 274.01, "other"),
    (274.01, 276.01, "bite"),
    (276.01, 295.01, "other"),
    (295.01, 297.01, "bite"),
    (297.01, 307.01, "other"),
    (307.01, 310.01, "bite"),
    (310.01, 322.01, "other"),
    (322.01, 324.01, "bite"),
    (324.01, 342.01, "other"),
    (342.01, 400.00, "other"),
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