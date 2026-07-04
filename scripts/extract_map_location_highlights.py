#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从monobehaviour JSON文件中提取MapLocationHighlight-开头文件的locationDesc到CSV文件
"""

import json
import csv
import os
from pathlib import Path

# 路径配置
MONOBEHAVIOUR_FOLDER = r'D:\SteamLibrary\steamapps\common\monobehaviour'
RESOURCES_FOLDER = r'D:\projects\RhellHan\resources'
OUTPUT_CSV = os.path.join(RESOURCES_FOLDER, 'map_location_highlight.csv')


def main():
    print("=" * 70)
    print("从 MonoBehaviour JSON 提取 MapLocationHighlight locationDesc")
    print("=" * 70)
    print(f"源文件夹: {MONOBEHAVIOUR_FOLDER}")
    print(f"输出文件: {OUTPUT_CSV}\n")

    if not os.path.isdir(MONOBEHAVIOUR_FOLDER):
        print(f"错误: 文件夹不存在: {MONOBEHAVIOUR_FOLDER}")
        return

    os.makedirs(RESOURCES_FOLDER, exist_ok=True)

    # 收集 MapLocationHighlight- 开头的JSON文件
    json_files = sorted(Path(MONOBEHAVIOUR_FOLDER).glob('MapLocationHighlight-*.json'))
    print(f"找到 {len(json_files)} 个 MapLocationHighlight- 开头的JSON文件\n")

    if not json_files:
        print("没有找到匹配的JSON文件")
        return


    unique_descriptions = set()

    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            desc = data.get('locationDesc')
            # 只判断 desc 是否为非空字符串，不去除首尾空白
            if desc and isinstance(desc, str) and desc != '':
                unique_descriptions.add(desc)

        except Exception as e:
            print(f"无法读取 {json_file.name}: {e}")
            continue

    if not unique_descriptions:
        print("未提取到任何有效的 locationDesc")
        return

    # 排序以保持输出稳定
    sorted_descriptions = sorted(list(unique_descriptions))

    try:
        with open(OUTPUT_CSV, 'w', encoding='utf-8', newline='') as csvfile:
            writer = csv.writer(csvfile)
            # 根据用户要求，放两列相同的值
            for desc in sorted_descriptions:
                writer.writerow([desc, desc])
        print(f"提取完成！共提取 {len(sorted_descriptions)} 条去重后的描述。")
        print(f"CSV文件已保存至: {OUTPUT_CSV}")
    except Exception as e:
        print(f"写入 CSV 文件失败: {e}")


if __name__ == '__main__':
    main()
