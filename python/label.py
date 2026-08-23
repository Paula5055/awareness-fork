import csv
import os

# ── Settings ──────────────────────────────────────────────
INPUT_FILE  = "data/paula/raw/mum_toast_01.csv"
OUTPUT_FILE = "data/paula/labeled/mum_toast_01_labeled.csv"

# ── Labels (start_sec, end_sec, label) ────────────────────
LABELS = [
    (4.49, 8.49, "other"),
    (8.49, 9.99, "other"),
    (9.99, 11.99, "bite"),
    (11.99, 24.99, "other"),
    (24.99, 27.49, "other"),
    (27.49, 33.49, "bite"),
    (33.49, 40.74, "other"),
    (40.74, 43.49, "other"),
    (43.49, 45.49, "bite"),
    (45.49, 54.99, "other"),
    (54.99, 57.49, "other"),
    (57.49, 70.49, "bite"),
    (70.49, 77.99, "other"),
    (77.99, 79.49, "other"),
    (79.49, 90.99, "bite"),
    (90.99, 94.49, "other"),
    (94.49, 98.49, "bite"),
    (98.49, 109.49, "other"),
    (109.49, 111.49, "other"),
    (111.49, 120.49, "bite"),
    (120.49, 130.49, "other"),
    (130.49, 132.49, "other"),
    (132.49, 136.49, "bite"),
    (136.49, 142.49, "other"),
    (142.49, 144.49, "other"),
    (144.49, 148.49, "bite"),
    (148.49, 154.49, "other"),
    (154.49, 156.49, "other"),
    (156.49, 158.49, "bite"),
    (158.49, 166.49, "other"),
    (166.49, 169.49, "other"),
    (169.49, 180.49, "bite"),
    (180.49, 182.49, "other"),
    (182.49, 187.49, "bite"),
    (187.49, 999.0, "other"),
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