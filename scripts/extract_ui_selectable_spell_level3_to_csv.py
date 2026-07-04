#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import json
from pathlib import Path

MONOBEHAVIOUR_DIR = Path(r"D:\SteamLibrary\steamapps\common\monobehaviour")
GAMEOBJECT_DIR = Path(r"D:\SteamLibrary\steamapps\common\GameObject")
RESOURCES_DIR = Path(r"D:\projects\RhellHan\resources")

OUTPUT_NAME_CSV = RESOURCES_DIR / "selectable_spell_name.csv"
OUTPUT_DESCRIPTION_CSV = RESOURCES_DIR / "selectable_spell_description.csv"


def safe_read_json(path: Path):
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[WARN] 读取失败: {path} -> {e}")
        return None


def find_ui_selectable_spell_files():
    files = list(MONOBEHAVIOUR_DIR.glob("UISelectableSpell-level3-*.json"))
    # 去重并按文件名排序
    return sorted(set(files), key=lambda p: p.name)


def find_gameobject_name_by_pathid(path_id):
    if path_id is None:
        return ""

    candidates = list(GAMEOBJECT_DIR.glob(f"*-{path_id}.json"))
    if not candidates:
        return ""

    # 优先 level3 文件，再退回第一个候选
    level3_candidates = [p for p in candidates if "-level3-" in p.name]
    target = level3_candidates[0] if level3_candidates else candidates[0]

    gameobject_data = safe_read_json(target)
    if not isinstance(gameobject_data, dict):
        return ""

    name = gameobject_data.get("m_Name", "")
    return name if isinstance(name, str) else ""


def build_rows():
    ui_files = find_ui_selectable_spell_files()
    name_rows = []
    description_rows = []

    print(f"找到 {len(ui_files)} 个 UISelectableSpell level3 文件")

    for file_path in ui_files:
        data = safe_read_json(file_path)
        if not isinstance(data, dict):
            continue

        path_id = data.get("m_GameObject", {}).get("m_PathID")
        rune_description = data.get("runeDescription", "")
        if not isinstance(rune_description, str):
            rune_description = ""

        m_name = find_gameobject_name_by_pathid(path_id)
        if not m_name:
            print(f"[WARN] 未找到 GameObject 名称: {file_path.name}, m_PathID={path_id}")

        name_rows.append([m_name, m_name])
        description_rows.append([f"{m_name}|||{rune_description}", rune_description])

    return name_rows, description_rows


def write_csv(path: Path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerows(rows)


def main():
    if not MONOBEHAVIOUR_DIR.exists():
        print(f"[ERROR] monobehaviour 文件夹不存在: {MONOBEHAVIOUR_DIR}")
        return
    if not GAMEOBJECT_DIR.exists():
        print(f"[ERROR] GameObject 文件夹不存在: {GAMEOBJECT_DIR}")
        return

    name_rows, description_rows = build_rows()

    write_csv(OUTPUT_NAME_CSV, name_rows)
    write_csv(OUTPUT_DESCRIPTION_CSV, description_rows)

    print(f"已写入: {OUTPUT_NAME_CSV} ({len(name_rows)} 行)")
    print(f"已写入: {OUTPUT_DESCRIPTION_CSV} ({len(description_rows)} 行)")


if __name__ == "__main__":
    main()
