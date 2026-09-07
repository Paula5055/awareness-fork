import csv
import os

# ── Settings ──────────────────────────────────────────────
INPUT_FILE  = "data/paula/raw/mum_bratwurst_01.csv"
OUTPUT_FILE = "data/paula/labeled/mum_bratwurst_01_labeled.csv"

# ── Labels (start_sec, end_sec, label) ────────────────────
LABELS = [
    (10.79, 16.79, "other"),
    (16.79, 18.79, "bite"),
    (18.79, 31.79, "other"),
    (31.79, 32.79, "bite"),
    (32.79, 42.79, "other"),
    (42.79, 43.79, "bite"),
    (43.79, 55.79, "other"),
    (55.79, 56.79, "bite"),
    (56.79, 67.79, "other"),
    (67.79, 69.79, "bite"),
    (69.79, 83.79, "other"),
    (83.79, 84.79, "bite"),
    (84.79, 99.79, "other"),
    (99.79, 100.79, "bite"),
    (100.79, 112.79, "other"),
    (112.79, 114.79, "bite"),
    (114.79, 124.79, "other"),
    (124.79, 126.79, "bite"),
    (126.79, 139.79, "other"),
    (139.79, 141.79, "bite"),
    (141.79, 159.79, "other"),
    (159.79, 161.79, "bite"),
    (161.79, 171.79, "other"),
    (171.79, 173.79, "bite"),
    (173.79, 189.79, "other"),
    (189.79, 190.79, "bite"),
    (190.79, 198.79, "other"),
    (198.79, 200.79, "bite"),
    (200.79, 221.79, "other"),
    (221.79, 222.79, "bite"),
    (222.79, 233.79, "other"),
    (233.79, 235.79, "bite"),
    (235.79, 249.79, "other"),
    (249.79, 251.79, "bite"),
    (251.79, 264.79, "other"),
    (264.79, 265.79, "bite"),
    (265.79, 999.0, "other")
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