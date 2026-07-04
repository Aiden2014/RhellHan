#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从v2 monobehaviour JSON文件中提取Text-开头文件的m_Text，
并与旧版text.csv中已有的中文翻译合并，输出新的text.csv。
"""

import json
import csv
import os
from pathlib import Path

V2_FOLDER = r'D:\SteamLibrary\steamapps\common\monobehaviour\v2'
OLD_TEXT_CSV = r'D:\SteamLibrary\steamapps\common\Rhell\BepInEx\plugins\resources\text.csv'
OUTPUT_CSV = r'D:\projects\RhellHan\resources\text.csv'
RESOURCES_FOLDER = r'D:\projects\RhellHan\resources'


def load_old_translations(csv_path):
    """加载旧版text.csv中的翻译，返回 {english_text: chinese_translation}。"""
    translations = {}
    if not os.path.isfile(csv_path):
        print(f"警告: 旧翻译文件不存在: {csv_path}")
        return translations

    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) >= 1:
                english = row[0]
                chinese = row[2] if len(row) >= 3 and row[2].strip() else None
                translations[english] = chinese

    return translations


def main():
    print("=" * 70)
    print("从 v2 MonoBehaviour JSON 提取 Text m_Text 并合并翻译")
    print("=" * 70)
    print(f"源文件夹:   {V2_FOLDER}")
    print(f"旧翻译文件: {OLD_TEXT_CSV}")
    print(f"输出文件:   {OUTPUT_CSV}\n")

    if not os.path.isdir(V2_FOLDER):
        print(f"错误: 文件夹不存在: {V2_FOLDER}")
        return

    os.makedirs(RESOURCES_FOLDER, exist_ok=True)

    print("加载旧翻译...")
    old_translations = load_old_translations(OLD_TEXT_CSV)
    translated_count = sum(1 for v in old_translations.values() if v is not None)
    print(f"加载了 {len(old_translations)} 条旧记录，其中 {translated_count} 条有中文翻译\n")

    json_files = sorted(Path(V2_FOLDER).glob('Text-*.json'))
    print(f"找到 {len(json_files)} 个 Text- 开头的JSON文件\n")

    if not json_files:
        print("没有找到匹配的JSON文件")
        return

    all_rows = []
    seen = set()
    total_count = 0
    reused_count = 0
    new_count = 0

    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            print(f"无法读取 {json_file.name}: {e}")
            continue

        m_text = data.get('m_Text', '')
        if isinstance(m_text, str) and m_text.strip():
            total_count += 1
            if m_text not in seen:
                seen.add(m_text)
                chinese = old_translations.get(m_text)
                if chinese:
                    reused_count += 1
                else:
                    new_count += 1
                all_rows.append((m_text, chinese))

    print(f"提取到 {total_count} 条文本，去重后 {len(all_rows)} 条")
    print(f"复用旧翻译: {reused_count}  新文本（待翻译）: {new_count}")

    try:
        with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.writer(csvfile)
            for english, chinese in all_rows:
                if chinese:
                    writer.writerow([english, english, chinese])
                else:
                    writer.writerow([english, english])

        print(f"\n成功写入 CSV 文件: {OUTPUT_CSV}")
        print(f"总行数: {len(all_rows)}")
    except Exception as e:
        print(f"\n写入CSV文件失败: {e}")


if __name__ == '__main__':
    main()
