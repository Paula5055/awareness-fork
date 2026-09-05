import csv
import os

# ── Settings ──────────────────────────────────────────────
INPUT_FILE  = "data/paula/raw/mum_sandwich_01.csv"
OUTPUT_FILE = "data/paula/labeled/mum_sandwich_01_labeled.csv"

# ── Labels (start_sec, end_sec, label) ────────────────────
LABELS = [
    (18.05, 26.05, "other"),
    (26.05, 29.05, "bite"),
    (29.05, 38.05, "other"),
    (38.05, 40.05, "bite"),
    (40.05, 55.05, "other"),
    (55.05, 56.05, "bite"),
    (56.05, 67.05, "other"),
    (67.05, 69.05, "bite"),
    (69.05, 87.05, "other"),
    (87.05, 89.05, "bite"),
    (89.05, 103.05, "other"),
    (103.05, 104.05, "bite"),
    (104.05, 116.05, "other"),
    (116.05, 118.05, "bite"),
    (118.05, 130.05, "other"),
    (130.05, 132.05, "bite"),
    (132.05, 150.05, "other"),
    (150.05, 152.05, "bite"),
    (152.05, 166.05, "other"),
    (166.05, 168.05, "bite"),
    (168.05, 181.05, "other"),
    (181.05, 183.05, "bite"),
    (183.05, 202.05, "other"),
    (202.05, 204.05, "bite"),
    (204.05, 217.05, "other"),
    (217.05, 219.05, "bite"),
    (219.05, 238.05, "other"),
    (238.05, 239.05, "bite"),
    (239.05, 257.05, "other"),
    (257.05, 258.05, "bite"),
    (258.05, 270.05, "other"),
    (270.05, 271.05, "bite"),
    (271.05, 283.05, "other"),
    (283.05, 284.05, "bite"),   
    (284.05, 303.05, "other"),
    (303.05, 304.05, "bite"),
    (304.05, 318.05, "other"),
    (318.05, 319.05, "bite"),
    (319.05, 336.05, "other"),
    (336.05, 337.55, "bite"),
    (337.55, 350.05, "other"),
    (350.05, 351.05, "bite"),
    (351.05, 363.05, "other"),
    (363.05, 365.05, "bite"),
    (365.05, 374.05, "other"),
    (374.05, 376.05, "bite"),
    (376.05, 999.0, "other"),
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