#!/usr/bin/env python3
"""
Create a list of 'false confidence' tokens for an OCR'd Middle Dutch text,
using a reference corpus (e.g. CorpusMiddelnederlands_1.0).

This script:

  - Builds a frequency dictionary from the reference corpus.
  - Reads an OCR target text and counts tokens.
  - Selects ONLY tokens that:
        * do NOT appear in the reference corpus, and
        * are NOT legitimate Roman numerals.
  - Sorts them by frequency in the target corpus (lowest → highest).
  - Writes them to a CSV.

Usage example (macOS):

    python3 ocr_middle_dutch_false_confidence_list.py \
        "/Users/annchapmanprice/Desktop/CorpusMiddelnederlands_1.0" \
        page1_ocr.txt \
        page1_false_confidence_list.csv
"""

import re
import csv
import sys
from collections import Counter
from pathlib import Path


def tokenize(text: str):
    """
    Very simple tokenizer:
    - keeps sequences of letters (including extended Latin) as words
    - drops punctuation and digits
    - lowercases everything.
    """
    tokens = re.findall(r"[A-Za-zÀ-ÿ]+", text)
    return [t.lower() for t in tokens]


def build_reference_counts(ref_dir: Path) -> Counter:
    """
    Walk through reference corpus files in ref_dir (recursively),
    tokenize them, and build a word frequency Counter.

    IMPORTANT:
      Adjust `allowed_exts` to match your actual corpus file extensions
      if needed. This is currently set to common text-like formats.
    """
    counts = Counter()

    # Adjust this set if your corpus uses different file extensions.
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


def is_roman_numeral(word: str) -> bool:
    """
    Return True if `word` is a 'legitimate' Roman numeral.

    Here we use a simple rule:
      - The word consists ONLY of the letters I, V, X, L, C, D, M
        (upper or lower case).

    This will treat tokens like 'i', 'ii', 'iv', 'x', 'xv', 'mcd' as Roman numerals
    and exclude them from the 'false confidence' list.
    """
    return bool(re.fullmatch(r"[ivxlcdmIVXLCDM]+", word))


def build_false_confidence_list(ref_dir: str, target_path: str, output_path: str):
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

    # 3) Select only tokens NOT in reference corpus AND not Roman numerals
    rows = []
    for word, freq_target in target_counts.items():
        freq_ref = ref_counts.get(word, 0)

        # Skip words that appear in the reference corpus
        if freq_ref > 0:
            continue

        # Skip tokens that are legitimate Roman numerals
        if is_roman_numeral(word):
            continue

        rows.append({
            "word": word,
            "frequency_in_target": freq_target,
        })

    # 4) Sort by frequency_in_target (lowest → highest), then alphabetically
    rows.sort(key=lambda r: (r["frequency_in_target"], r["word"]))

    # 5) Write CSV
    fieldnames = ["word", "frequency_in_target"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Done. False-confidence list written to: {output_path}")


def main():
    if len(sys.argv) != 4:
        print(
            "Usage: python3 ocr_middle_dutch_false_confidence_list.py "
            "REF_CORPUS_DIR TARGET_OCR_TEXT OUTPUT_CSV"
        )
        sys.exit(1)

    ref_dir = sys.argv[1]
    target_path = sys.argv[2]
    output_path = sys.argv[3]

    build_false_confidence_list(ref_dir, target_path, output_path)


if __name__ == "__main__":
    main()
