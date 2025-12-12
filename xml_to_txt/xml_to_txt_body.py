#!/usr/bin/env python3
import re
from pathlib import Path
from xml.etree import ElementTree as ET

def extract_body_text(xml_path: Path) -> str:
    tree = ET.parse(xml_path)
    root = tree.getroot()

    # Find <body> tag (case-insensitive search)
    body = None
    for elem in root.iter():
        if elem.tag.lower().endswith("body"):
            body = elem
            break

    if body is None:
        # fallback: no <body>, dump everything
        text = ''.join(root.itertext())
    else:
        text = ''.join(body.itertext())

    # collapse whitespace
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def convert_folder(input_folder: str):
    input_folder = Path(input_folder)

    for xml_file in input_folder.rglob("*.xml"):
        text = extract_body_text(xml_file)
        out_file = xml_file.with_suffix(".txt")  # same folder, replace .xml with .txt
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"Converted {xml_file} → {out_file}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Convert XML files to plain text (body only).")
    parser.add_argument("input_folder", help="Folder containing XML files")
    args = parser.parse_args()
    convert_folder(args.input_folder)
