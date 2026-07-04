#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从 monobehaviour/v2 中提取 ChallengeMenu 文件的 ChallengeName 字段
"""

import csv
import json
from pathlib import Path

MONOBEHAVIOUR_DIR = Path(r"D:\SteamLibrary\steamapps\common\monobehaviour\v2")
RESOURCES_DIR = Path(r"D:\projects\RhellHan\resources")

OUTPUT_CSV = RESOURCES_DIR / "challenge_menu.csv"


def safe_read_json(path: Path):
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[WARN] 读取失败: {path} -> {e}")
        return None


def build_rows():
    files = sorted(MONOBEHAVIOUR_DIR.glob("ChallengeMenu-level*.json"))
    seen = set()
    rows = []

    print(f"找到 {len(files)} 个 ChallengeMenu 文件")

    for file_path in files:
        data = safe_read_json(file_path)
        if not isinstance(data, dict):
            continue

        challenges = data.get("challenges", {})
        array = challenges.get("Array", []) if isinstance(challenges, dict) else []

        for entry in array:
            name = entry.get("ChallengeName", "") if isinstance(entry, dict) else ""
            if isinstance(name, str) and name.strip() and name not in seen:
                seen.add(name)
                rows.append([name, name, ""])

    return rows


def write_csv(path: Path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerows(rows)


def main():
    if not MONOBEHAVIOUR_DIR.exists():
        print(f"[ERROR] monobehaviour/v2 文件夹不存在: {MONOBEHAVIOUR_DIR}")
        return

    rows = build_rows()

    write_csv(OUTPUT_CSV, rows)

    print(f"已写入: {OUTPUT_CSV} ({len(rows)} 行)")


if __name__ == "__main__":
    main()
