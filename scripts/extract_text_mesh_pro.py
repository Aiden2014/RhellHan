#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从monobehaviour/v2 JSON文件中提取TextMeshPro-level开头文件的m_text到CSV文件
"""

import json
import csv
import os
from pathlib import Path

# 路径配置
MONOBEHAVIOUR_FOLDER = r'D:\SteamLibrary\steamapps\common\monobehaviour\v2'
RESOURCES_FOLDER = r'D:\projects\RhellHan\resources'
OUTPUT_CSV = os.path.join(RESOURCES_FOLDER, 'text_mesh_pro.csv')


def main():
    print("=" * 70)
    print("从 MonoBehaviour/v2 JSON 提取 TextMeshPro m_text")
    print("=" * 70)
    print(f"源文件夹: {MONOBEHAVIOUR_FOLDER}")
    print(f"输出文件: {OUTPUT_CSV}\n")

    if not os.path.isdir(MONOBEHAVIOUR_FOLDER):
        print(f"错误: 文件夹不存在: {MONOBEHAVIOUR_FOLDER}")
        return

    os.makedirs(RESOURCES_FOLDER, exist_ok=True)

    # 收集 TextMeshPro-level 开头的JSON文件
    json_files = sorted(Path(MONOBEHAVIOUR_FOLDER).glob('TextMeshPro-level*.json'))
    print(f"找到 {len(json_files)} 个 TextMeshPro-level 开头的JSON文件\n")

    if not json_files:
        print("没有找到匹配的JSON文件")
        return

    all_texts = []
    seen = set()
    total_count = 0

    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            print(f"无法读取 {json_file.name}: {e}")
            continue

        m_text = data.get('m_text', '')
        if isinstance(m_text, str) and m_text.strip():
            total_count += 1
            if m_text not in seen:
                seen.add(m_text)
                all_texts.append(m_text)

    print(f"提取到 {total_count} 条文本，去重后 {len(all_texts)} 条")

    # 写入CSV文件（无表头，第一列和第二列内容相同，第三列空）
    try:
        with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.writer(csvfile)
            for text in all_texts:
                writer.writerow([text, text, ''])

        print(f"\n成功写入 CSV 文件: {OUTPUT_CSV}")
        print(f"总行数: {len(all_texts)}")
    except Exception as e:
        print(f"\n写入CSV文件失败: {e}")


if __name__ == '__main__':
    main()
