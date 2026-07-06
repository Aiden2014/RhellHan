#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
Extract unique non-ASCII characters from CSV files.

Default input:
    D:\SteamLibrary\steamapps\common\Rhell\BepInEx\plugins\resources

Default output:
    <project root>\resources\unique_non_ascii_chars.txt

Usage:
    py scripts/extract_unique_non_ascii_chars.py
    py scripts/extract_unique_non_ascii_chars.py --recursive
    py scripts/extract_unique_non_ascii_chars.py --resources "D:\path\resources"
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path


DEFAULT_RESOURCES_DIR = Path(
    r"D:\SteamLibrary\steamapps\common\Rhell\BepInEx\plugins\resources"
)


def configure_output_encoding() -> None:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="backslashreplace")


def parse_args() -> argparse.Namespace:
    project_root = Path(__file__).resolve().parent.parent
    default_output = project_root / "resources" / "unique_non_ascii_chars.txt"

    parser = argparse.ArgumentParser(
        description=(
            "Extract unique non-ASCII characters from CSV files and write them "
            "to resources/unique_non_ascii_chars.txt."
        )
    )
    parser.add_argument(
        "--resources",
        type=Path,
        default=DEFAULT_RESOURCES_DIR,
        help=f"Directory containing CSV files. Default: {DEFAULT_RESOURCES_DIR}",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=default_output,
        help=f"Output text file. Default: {default_output}",
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Search CSV files recursively under the resources directory.",
    )
    parser.add_argument(
        "--encoding",
        default="utf-8-sig",
        help="CSV text encoding. Default: utf-8-sig",
    )
    return parser.parse_args()


def iter_csv_files(resources_dir: Path, recursive: bool) -> list[Path]:
    pattern = "**/*.csv" if recursive else "*.csv"
    return sorted(path for path in resources_dir.glob(pattern) if path.is_file())


def collect_non_ascii_chars(csv_files: list[Path], encoding: str) -> set[str]:
    chars: set[str] = set()

    for csv_file in csv_files:
        with csv_file.open("r", encoding=encoding, newline="") as handle:
            reader = csv.reader(handle)
            for row in reader:
                for cell in row:
                    chars.update(char for char in cell if ord(char) > 0x7F)

    return chars


def main() -> int:
    configure_output_encoding()
    args = parse_args()

    resources_dir = args.resources.expanduser()
    output_file = args.output.expanduser()

    if not resources_dir.is_dir():
        print(f"Error: resources directory does not exist: {resources_dir}", file=sys.stderr)
        return 2

    csv_files = iter_csv_files(resources_dir, args.recursive)
    if not csv_files:
        print(f"Error: no CSV files found in: {resources_dir}", file=sys.stderr)
        return 2

    chars = collect_non_ascii_chars(csv_files, args.encoding)
    sorted_chars = sorted(chars, key=ord)

    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text("".join(sorted_chars), encoding="utf-8")

    print(f"CSV files checked: {len(csv_files)}")
    print(f"Unique non-ASCII chars found: {len(sorted_chars)}")
    print(f"Saved to: {output_file}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
