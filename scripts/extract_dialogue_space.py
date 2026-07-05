#!/usr/bin/env python3
"""Extract whitespace-only dialogue entries from InteractDialogue JSONs into dialogue_space.csv.

For each InteractDialogue-level*.json:
1. Find dialogue entries in dialogues.Array where the "dialogue" field is whitespace-only
2. Use another non-whitespace dialogue from the same array to look up in dialogue_filtered.csv
3. Extract the first two |||-segments from the matching CSV row
4. Construct key: {first_two}|||{array_index}|||{whitespace}
5. Output: col1=key, col2=whitespace, col3=whitespace
"""

import csv
import json
import os
import re
from collections import defaultdict

V2_DIR = r"D:\SteamLibrary\steamapps\common\monobehaviour\v2"
RESOURCES_DIR = r"D:\projects\RhellHan\resources"
DIALOGUE_FILTERED = os.path.join(RESOURCES_DIR, "dialogue_filtered.csv")
OUTPUT_FILE = os.path.join(RESOURCES_DIR, "dialogue_space.csv")


def build_dialogue_lookup():
    """Build a dict mapping dialogue_text -> list of (first_two_segments,)."""
    lookup = defaultdict(list)

    with open(DIALOGUE_FILTERED, "r", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) < 2:
                continue
            col1 = row[0]
            col2 = row[1]
            parts = col1.split("|||")
            if len(parts) < 2:
                continue
            first_two = f"{parts[0]}|||{parts[1]}"
            lookup[col2].append(first_two)

    return lookup


def extract_level_and_id(filename):
    """Extract (level_str, path_id) from filename like 'InteractDialogue-level46-5587.json'."""
    m = re.search(r"(level\d+)-(\d+)\.json$", filename)
    if m:
        return m.group(1), m.group(2)
    return None, None


def is_whitespace_only(s):
    """Check if a string is non-empty and contains only whitespace."""
    return bool(s) and s.isspace()


def main():
    lookup = build_dialogue_lookup()
    print(f"Loaded {len(lookup)} unique dialogue texts from dialogue_filtered.csv")

    interact_files = sorted(
        f for f in os.listdir(V2_DIR) if f.startswith("InteractDialogue-")
    )
    print(f"Found {len(interact_files)} InteractDialogue files")

    rows = []
    seen_keys = set()
    processed = 0
    not_found = []
    no_non_space = []

    for filename in interact_files:
        filepath = os.path.join(V2_DIR, filename)
        level_str, path_id = extract_level_and_id(filename)
        expected_prefix = f"{level_str}|||{path_id}"

        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        dialogues = data.get("dialogues", {}).get("Array", [])
        if not dialogues:
            continue

        # Find all whitespace entries and all non-whitespace entries
        space_entries = []  # (index, whitespace_string)
        non_space_texts = []  # dialogue strings that are not whitespace

        for idx, entry in enumerate(dialogues):
            text = entry.get("dialogue", "")
            if is_whitespace_only(text):
                space_entries.append((idx, text))
            elif text.strip():
                non_space_texts.append(text)

        if not space_entries:
            continue

        if not non_space_texts:
            no_non_space.append(filename)
            continue

        # Try to find a CSV match whose prefix agrees with the filename
        first_two = None
        for text in non_space_texts:
            matches = lookup.get(text)
            if matches:
                exact = [m for m in matches if m == expected_prefix]
                if exact:
                    first_two = exact[0]
                    break

        if first_two is None:
            not_found.append(
                f"{filename}: no CSV match with prefix {expected_prefix}"
            )
            continue

        for idx, space_text in space_entries:
            key = f"{first_two}|||{idx}|||{space_text}"
            if key in seen_keys:
                continue
            seen_keys.add(key)
            rows.append((key, space_text, space_text))

        processed += 1

    with open(OUTPUT_FILE, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        for row in rows:
            writer.writerow(row)

    print(f"\nFound whitespace dialogues in {processed} files")
    print(f"Wrote {len(rows)} rows to {OUTPUT_FILE}")

    if not_found:
        print(f"\nNo CSV match for any non-space dialogue ({len(not_found)}):")
        for msg in not_found:
            print(f"  {msg}")

    if no_non_space:
        print(f"\nFiles with only whitespace dialogues ({len(no_non_space)}):")
        for msg in no_non_space:
            print(f"  {msg}")

    if not_found or no_non_space:
        print("\nDone with warnings.")
    else:
        print("Done.")


if __name__ == "__main__":
    main()
