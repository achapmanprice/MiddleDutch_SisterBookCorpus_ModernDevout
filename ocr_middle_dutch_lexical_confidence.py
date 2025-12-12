#!/usr/bin/env python3
"""
Compute simple 'lexical confidence' values for an OCR'd Middle Dutch text,
using a reference corpus (CorpusMiddelnederlands_1.0) on your machine.

- Step 1: Build word frequency dictionary from reference corpus.
- Step 2: Compare words in the target OCR text to that dictionary.
- Step 3: Output CSV report with lexical confidence per word.

Usage (example on macOS):
    python3 ocr_middle_dutch_lexical_confidence.py \
        "/Users/annchapmanprice/Desktop/CorpusMiddelnederlands_1.0" \
        page1_ocr.txt \
        page1_lexical_report.csv
"""

import re
import csv
import sys
from collections import Counter
from pathlib import Path
from math import log


def tokenize(text: str):
    """
    Very simple tokenizer:
    - keeps sequences of letters (including extended Latin) as words
    - drops punctuation and digits
    - lowercases everything

    You can later refine this for Middle Dutch-specific normalization
    (e.g. u/v, i/j, etc.) if you like.
    """
    tokens = re.findall(r"[A-Za-zÀ-ÿ]+", text)
    return [t.lower() for t in tokens]


def build_reference_counts(ref_dir: Path) -> Counter:
    """
    Walk through reference corpus files in ref_dir (recursively),
    tokenize them, and build a word frequency Counter.

    IMPORTANT:
      Adjust `allowed_exts` to match your actual corpus file extensions.
      You can check extensions by running, in Terminal:

          cd "/Users/annchapmanprice/Desktop/CorpusMiddelnederlands_1.0"
          find . -maxdepth 2 -type f | head
    """
    counts = Counter()

    # 👉 Edit this set if your corpus uses different extensions.
    # For GTB-related corpora it's often .xml or .vrt, but confirm via `find`.
    allowed_exts = {".txt", ".xml", ".vrt", ".csv", ".tsv"}

    ref_files = [
        p for p in ref_dir.rglob("*")
        if p.is_file() and p.suffix.lower() in allowed_exts
    ]

    print(f"Found {len(ref_files)} reference files with allowed extensions.")

    for path in ref_files:
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            print(f"Warning: could not read {path}: {e}", file=sys.stderr)
            continue

        tokens = tokenize(text)
        counts.update(tokens)

    return counts


def compute_lexical_confidence(ref_counts: Counter, word: str) -> float:
    """
    Compute a simple lexical confidence score in [0, 1] for a word,
    based only on its frequency in the reference corpus.

    Design (simple but reasonable):
      - If word not in reference corpus: 0.0
      - Otherwise: log-scaled frequency divided by log-scaled max frequency

    This gives:
      - Very frequent words  -> scores close to 1
      - Rare but attested    -> small positive scores
      - Unattested           -> 0.0

    You can tweak this function later if you prefer a different scaling.
    """
    freq = ref_counts.get(word, 0)
    if freq == 0:
        return 0.0

    max_freq = max(ref_counts.values())
    if max_freq <= 0:
        return 0.0

    score = log(1 + freq) / log(1 + max_freq)
    return float(score)


def build_report(ref_dir: str, target_path: str, output_path: str):
    ref_dir_path = Path(ref_dir)
    target_file = Path(target_path)

    # 1) Build reference corpus counts
    print(f"Building reference counts from: {ref_dir_path}")
    ref_counts = build_reference_counts(ref_dir_path)
    print(f"Reference vocabulary size: {len(ref_counts)} words")

    # 2) Read and tokenize target OCR text
    print(f"Reading target OCR text: {target_file}")
    target_text = target_file.read_text(encoding="utf-8", errors="ignore")
    target_tokens = tokenize(target_text)
    target_counts = Counter(target_tokens)

    # 3) Prepare rows
    rows = []
    for word, freq_target in sorted(
        target_counts.items(),
        key=lambda wf: (-wf[1], wf[0])
    ):
        freq_ref = ref_counts.get(word, 0)
        in_ref = freq_ref > 0
        lexical_conf = compute_lexical_confidence(ref_counts, word)

        rows.append({
            "word": word,
            "frequency_in_target": freq_target,
            "frequency_in_reference": freq_ref,
            "in_reference": in_ref,
            "lexical_confidence": f"{lexical_conf:.4f}",
        })

    # 4) Write CSV
    fieldnames = [
        "word",
        "frequency_in_target",
        "frequency_in_reference",
        "in_reference",
        "lexical_confidence",
    ]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Done. Report written to: {output_path}")


def main():
    if len(sys.argv) != 4:
        print(
            "Usage: python3 ocr_middle_dutch_lexical_confidence.py "
            "REF_CORPUS_DIR TARGET_OCR_TEXT OUTPUT_CSV"
        )
        sys.exit(1)

    ref_dir = sys.argv[1]
    target_path = sys.argv[2]
    output_path = sys.argv[3]

    build_report(ref_dir, target_path, output_path)


if __name__ == "__main__":
    main()
