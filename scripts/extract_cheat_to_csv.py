#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从 monobehaviour/v2 中提取 UISelectableCheat-level 文件的 cheatTitle 和 cheatDescription
"""

import csv
import json
from pathlib import Path

MONOBEHAVIOUR_DIR = Path(r"D:\SteamLibrary\steamapps\common\monobehaviour\v2")
RESOURCES_DIR = Path(r"D:\projects\RhellHan\resources")

OUTPUT_TITLE_CSV = RESOURCES_DIR / "cheat_title.csv"
OUTPUT_DESCRIPTION_CSV = RESOURCES_DIR / "cheat_description.csv"


def safe_read_json(path: Path):
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[WARN] 读取失败: {path} -> {e}")
        return None


def find_cheat_files():
    files = list(MONOBEHAVIOUR_DIR.glob("UISelectableCheat-level*.json"))
    return sorted(set(files), key=lambda p: p.name)


def build_rows():
    cheat_files = find_cheat_files()
    seen = set()
    title_rows = []
    description_rows = []

    print(f"找到 {len(cheat_files)} 个 UISelectableCheat 文件")

    for file_path in cheat_files:
        data = safe_read_json(file_path)
        if not isinstance(data, dict):
            continue

        cheat_title = data.get("cheatTitle", "")
        cheat_description = data.get("cheatDescription", "")

        if not isinstance(cheat_title, str) or not cheat_title.strip():
            continue
        if not isinstance(cheat_description, str):
            cheat_description = ""

        if cheat_title not in seen:
            seen.add(cheat_title)
            title_rows.append([cheat_title, cheat_title, ""])
            description_rows.append([cheat_title, cheat_description, ""])

    return title_rows, description_rows


def write_csv(path: Path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerows(rows)


def main():
    if not MONOBEHAVIOUR_DIR.exists():
        print(f"[ERROR] monobehaviour/v2 文件夹不存在: {MONOBEHAVIOUR_DIR}")
        return

    title_rows, description_rows = build_rows()

    write_csv(OUTPUT_TITLE_CSV, title_rows)
    write_csv(OUTPUT_DESCRIPTION_CSV, description_rows)

    print(f"已写入: {OUTPUT_TITLE_CSV} ({len(title_rows)} 行)")
    print(f"已写入: {OUTPUT_DESCRIPTION_CSV} ({len(description_rows)} 行)")


if __name__ == "__main__":
    main()
