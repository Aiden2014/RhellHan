#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从 TextMeshProUGUI-level1-*.json 文件中提取 m_text 字段，去重后写入 CSV
"""

import json
import csv
import os
from pathlib import Path

V2_FOLDER = r'D:\SteamLibrary\steamapps\common\monobehaviour\v2'
RESOURCES_FOLDER = r'D:\projects\RhellHan\resources'
OUTPUT_CSV = os.path.join(RESOURCES_FOLDER, 'text_mesh_pro_ugui.csv')


def main():
    print("=" * 70)
    print("从 TextMeshProUGUI-level1-*.json 提取 m_text 字段")
    print("=" * 70)

    if not os.path.isdir(V2_FOLDER):
        print(f"错误: 文件夹不存在: {V2_FOLDER}")
        return

    os.makedirs(RESOURCES_FOLDER, exist_ok=True)

    seen = set()
    rows = []

    for json_file in sorted(Path(V2_FOLDER).glob('TextMeshProUGUI-level1-*.json')):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            text = data.get('m_text', '')
            if isinstance(text, str) and text.strip():
                t = text.strip()
                if t not in seen:
                    seen.add(t)
                    rows.append([t, t, ''])
        except Exception:
            pass

    print(f"去重后共 {len(rows)} 条")

    with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(rows)

    print(f"已写入: {OUTPUT_CSV}")


if __name__ == '__main__':
    main()
