#!/usr/bin/env python3
"""Extract DialogueChanger JSON data into dialogue_changer.csv.

For each DialogueChanger-*.json file:
1. Extract dialogue.m_PathID
2. Find InteractDialogue-level{level}-{pathID}.json
3. Take the first dialogue text from the dialogues array
4. Look up in dialogue_filtered.csv where col2 matches and col1's 3rd ||| segment = "0"
5. Assemble key: {first_two_segments}|||{changeLine}|||{NewDialogue}
"""

import csv
import json
import os
import re
import sys
from collections import defaultdict

V2_DIR = r"D:\SteamLibrary\steamapps\common\monobehaviour\v2"
RESOURCES_DIR = r"D:\projects\RhellHan\resources"
DIALOGUE_FILTERED = os.path.join(RESOURCES_DIR, "dialogue_filtered.csv")
OUTPUT_FILE = os.path.join(RESOURCES_DIR, "dialogue_changer.csv")


def build_dialogue_lookup():
    """Build a dict mapping dialogue_text -> list of (first_two_segments, full_col1)."""
    lookup = defaultdict(list)

    with open(DIALOGUE_FILTERED, "r", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) < 2:
                continue
            col1 = row[0]
            col2 = row[1]
            parts = col1.split("|||")
            if len(parts) < 3:
                continue
            if parts[2] != "0":
                continue
            first_two = f"{parts[0]}|||{parts[1]}"
            lookup[col2].append((first_two, col1))

    return lookup


def extract_level(filename):
    """Extract level number from filename like 'DialogueChanger-level27-3101.json'."""
    m = re.search(r"level(\d+)", filename)
    return m.group(0) if m else None


def main():
    lookup = build_dialogue_lookup()
    print(f"Loaded {len(lookup)} unique dialogue texts from dialogue_filtered.csv")

    changer_files = sorted(
        f for f in os.listdir(V2_DIR) if f.startswith("DialogueChanger-")
    )
    print(f"Found {len(changer_files)} DialogueChanger files")

    rows = []
    seen_keys = set()
    duplicates = 0
    errors = []
    missing_interact = []
    not_found = []

    for filename in changer_files:
        filepath = os.path.join(V2_DIR, filename)

        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        path_id = data.get("dialogue", {}).get("m_PathID")
        if path_id is None:
            errors.append(f"{filename}: no dialogue.m_PathID found")
            continue

        level_str = extract_level(filename)
        if level_str is None:
            errors.append(f"{filename}: could not extract level")
            continue

        interact_filename = f"InteractDialogue-{level_str}-{path_id}.json"
        interact_path = os.path.join(V2_DIR, interact_filename)

        if not os.path.exists(interact_path):
            missing_interact.append(f"{filename} -> {interact_filename}")
            continue

        with open(interact_path, "r", encoding="utf-8") as f:
            interact_data = json.load(f)

        dialogues = interact_data.get("dialogues", {}).get("Array", [])
        if not dialogues:
            errors.append(f"{interact_filename}: no dialogues found")
            continue

        first_dialogue = dialogues[0].get("dialogue", "")
        if not first_dialogue:
            errors.append(f"{interact_filename}: first dialogue is empty")
            continue

        matches = lookup.get(first_dialogue)
        if not matches:
            not_found.append(
                f"{filename}: dialogue text not found in CSV: {first_dialogue!r}"
            )
            continue

        if len(matches) > 1:
            print(
                f"ERROR: {filename}: multiple matches for dialogue text {first_dialogue!r}:"
            )
            for first_two, full_col1 in matches:
                print(f"  - {full_col1}")
            errors.append(
                f"{filename}: {len(matches)} matches for {first_dialogue!r}"
            )
            continue

        first_two_segments = matches[0][0]

        changed_array = data.get("changedD", {}).get("Array", [])
        for entry in changed_array:
            change_line = entry.get("changeLine", "")
            new_dialogue = entry.get("NewDialogue", "")
            key = f"{first_two_segments}|||{change_line}|||{new_dialogue}"
            if key in seen_keys:
                duplicates += 1
                continue
            seen_keys.add(key)
            rows.append((key, new_dialogue, ""))

    with open(OUTPUT_FILE, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        for row in rows:
            writer.writerow(row)

    print(f"\nWrote {len(rows)} rows to {OUTPUT_FILE} ({duplicates} duplicates skipped)")

    if missing_interact:
        print(f"\nMissing InteractDialogue files ({len(missing_interact)}):")
        for msg in missing_interact:
            print(f"  {msg}")

    if not_found:
        print(f"\nDialogue texts not found in CSV ({len(not_found)}):")
        for msg in not_found:
            print(f"  {msg}")

    if errors:
        print(f"\nErrors ({len(errors)}):")
        for msg in errors:
            print(f"  {msg}")

    if missing_interact or not_found or errors:
        print("\nDone with warnings.")
    else:
        print("Done.")


if __name__ == "__main__":
    main()
