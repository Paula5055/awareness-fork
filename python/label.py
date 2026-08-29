import csv
import os

# ── Settings ──────────────────────────────────────────────
INPUT_FILE  = "data/paula/raw/mum_rice_01.csv"
OUTPUT_FILE = "data/paula/labeled/mum_rice_01_labeled.csv"

# ── Labels (start_sec, end_sec, label) ────────────────────
LABELS = [
   (14.30, 18.30, "other"),
    (18.30, 27.30, "other"),
    (27.30, 28.80, "bite"),
    (28.80, 38.30, "other"),
    (38.30, 41.30, "bite"),
    (41.30, 59.30, "other"),
    (59.30, 62.30, "bite"),
    (62.30, 75.30, "other"),
    (75.30, 77.30, "bite"),
    (77.30, 88.30, "other"),
    (88.30, 90.30, "bite"),
    (90.30, 104.30, "other"),
    (104.30, 106.30, "bite"),
    (106.30, 115.30, "other"),
    (115.30, 117.30, "bite"),
    (117.30, 125.30, "other"),
    (125.30, 127.30, "bite"),
    (127.30, 139.30, "other"),
    (139.30, 141.30, "bite"),
    (141.30, 154.30, "other"),
    (154.30, 156.30, "bite"),
    (156.30, 167.30, "other"),
    (167.30, 170.30, "bite"),
    (170.30, 187.30, "other"),
    (187.30, 189.30, "bite"),
    (189.30, 200.30, "other"),
    (200.30, 203.30, "bite"),
    (203.30, 212.30, "other"),
    (212.30, 214.30, "bite"),
    (214.30, 225.30, "other"),
    (225.30, 227.30, "bite"),
    (227.30, 240.30, "other"),
    (240.30, 242.30, "bite"),
    (242.30, 259.30, "other"),
    (259.30, 261.30, "bite"),
    (261.30, 271.30, "other"),
    (271.30, 274.30, "bite"),
    (274.30, 289.30, "other"),
    (289.30, 291.30, "bite"),
    (291.30, 296.30, "other"),
    (296.30, 298.30, "bite"),
    (298.30, 414.30, "other"),
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