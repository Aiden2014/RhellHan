#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从UiStoryHandle JSON文件中提取summaries到CSV文件，并进行去重
"""

import json
import csv
import os
from pathlib import Path
from collections import defaultdict

# 路径配置
MONOBEHAVIOUR_FOLDER = r'D:\SteamLibrary\steamapps\common\monobehaviour'
RESOURCES_FOLDER = r'D:\projects\RhellHan\resources'
OUTPUT_CSV = os.path.join(RESOURCES_FOLDER, 'summary.csv')


def parse_filename(filename):
    """
    解析JSON文件名，提取组件
    格式: UiStoryHandle-{level}-{id}.json
    例如: UiStoryHandle-level3-28171.json
    返回: (level, id)
    """
    # 移除 .json 扩展名
    name_without_ext = filename.replace('.json', '')
    
    # 移除 UiStoryHandle- 前缀
    if not name_without_ext.startswith('UiStoryHandle-'):
        return None, None
    
    name_without_ext = name_without_ext[len('UiStoryHandle-'):]
    
    # 按 '-' 分割，从右边分割以确保只分出最后的id
    parts = name_without_ext.rsplit('-', 1)
    
    if len(parts) == 2:
        level = parts[0]  # level3
        id_num = parts[1]  # 28171
        return level, id_num
    
    return None, None


def extract_summaries_from_file(json_file):
    """
    从单个JSON文件中提取summaries
    返回: [(id_string, story_txt, title_story_combo), ...]
    """
    results = []
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"⚠️  无法读取 {os.path.basename(json_file)}: {e}")
        return results
    
    # 获取 summaries 数组
    summaries = data.get('summaries', {})
    if not isinstance(summaries, dict):
        return results
    
    summary_array = summaries.get('Array', [])
    if not isinstance(summary_array, list):
        return results
    
    filename = os.path.basename(json_file)
    level, id_num = parse_filename(filename)
    
    if level is None or id_num is None:
        print(f"⚠️  无法解析文件名格式: {filename}")
        return results
    
    # 提取每个summary
    for idx, summary_entry in enumerate(summary_array):
        if isinstance(summary_entry, dict):
            title = summary_entry.get('Title', '')
            story_txt = summary_entry.get('storyTxt', '')
            
            if isinstance(title, str) and isinstance(story_txt, str):
                # 第一列格式: level|||id|||idx|||title|||storyTxt
                id_string = f"{level}|||{id_num}|||{idx}|||{title}|||{story_txt}"
                # 用于比较的组合：title|||storyTxt
                title_story_combo = f"{title}|||{story_txt}"
                results.append((id_string, story_txt, title_story_combo))
    
    return results


def filter_and_deduplicate_summaries(all_summaries):
    """
    去重处理：
    - 按 level|||id 分组
    - 比较 title|||storyTxt 的组合是否相同
    - 保留翻译更多的数组
    """
    array_groups = defaultdict(list)  # array_id -> [(idx, id_string, story_txt, title_story_combo), ...]
    
    # 第一步：按数组分组
    for id_string, story_txt, title_story_combo in all_summaries:
        parts = id_string.split('|||')
        if len(parts) >= 3:
            array_id = f"{parts[0]}|||{parts[1]}"  # level|||id
            try:
                idx = int(parts[2])
                array_groups[array_id].append((idx, id_string, story_txt, title_story_combo))
            except ValueError:
                continue
    
    # 第二步：比较数组，找出内容相同的数组对
    arrays = list(array_groups.keys())
    merged = set()  # 记录已经处理过的数组
    output_rows = []
    
    for i, array_id1 in enumerate(arrays):
        if array_id1 in merged:
            continue
        
        group1 = sorted(array_groups[array_id1], key=lambda x: x[0])
        combos1 = [combo for _, _, _, combo in group1]
        trans_count1 = sum(1 for _, _, txt, _ in group1 if txt.strip())
        
        # 与其他数组比较，找出title|||storyTxt内容完全相同的
        duplicate_arrays = [array_id1]  # 包括自己
        
        for j in range(i + 1, len(arrays)):
            array_id2 = arrays[j]
            if array_id2 in merged:
                continue
            
            group2 = sorted(array_groups[array_id2], key=lambda x: x[0])
            combos2 = [combo for _, _, _, combo in group2]
            
            # 检查title|||storyTxt内容和顺序是否完全相同
            if len(combos1) == len(combos2) and combos1 == combos2:
                duplicate_arrays.append(array_id2)
                merged.add(array_id2)
        
        # 如果有重复数组，保留翻译最多的
        if len(duplicate_arrays) > 1:
            best_array_id = None
            best_trans_count = -1
            
            for dup_id in duplicate_arrays:
                group = sorted(array_groups[dup_id], key=lambda x: x[0])
                trans_count = sum(1 for _, _, txt, _ in group if txt.strip())
                if trans_count > best_trans_count:
                    best_trans_count = trans_count
                    best_array_id = dup_id
            
            # 只保留翻译最多的数组的所有行
            group = sorted(array_groups[best_array_id], key=lambda x: x[0])
            for _, id_string, story_txt, _ in group:
                first_col = id_string.split('|||', 1)[1]
                output_rows.append([first_col, story_txt, ''])
        else:
            # 没有重复，直接加入此数组的所有行
            group = sorted(array_groups[array_id1], key=lambda x: x[0])
            for _, id_string, story_txt, _ in group:
                first_col = id_string.split('|||', 1)[1]
                output_rows.append([first_col, story_txt, ''])
        
        merged.add(array_id1)
    
    return output_rows


def main():
    """
    主程序
    """
    print("=" * 70)
    print("从 UiStoryHandle JSON 提取 Summaries 并去重")
    print("=" * 70)
    print(f"源文件夹: {MONOBEHAVIOUR_FOLDER}")
    print(f"输出文件: {OUTPUT_CSV}\n")
    
    # 检查文件夹是否存在
    if not os.path.isdir(MONOBEHAVIOUR_FOLDER):
        print(f"❌ 错误: 文件夹不存在: {MONOBEHAVIOUR_FOLDER}")
        return
    
    if not os.path.isdir(RESOURCES_FOLDER):
        print(f"⚠️  创建输出文件夹: {RESOURCES_FOLDER}")
        os.makedirs(RESOURCES_FOLDER, exist_ok=True)
    
    # 收集所有UiStoryHandle JSON文件
    json_files = sorted([f for f in Path(MONOBEHAVIOUR_FOLDER).glob('*.json') 
                        if f.name.startswith('UiStoryHandle-')])
    print(f"找到 {len(json_files)} 个UiStoryHandle JSON文件\n")
    
    if not json_files:
        print("❌ 没有找到UiStoryHandle JSON文件")
        return
    
    # 提取数据
    all_summaries = []
    processed_files = 0
    total_summaries = 0
    
    for json_file in json_files:
        summaries = extract_summaries_from_file(str(json_file))
        if summaries:
            all_summaries.extend(summaries)
            processed_files += 1
            total_summaries += len(summaries)
            print(f"✓ {json_file.name}: {len(summaries)} 条摘要")
    
    print(f"\n📊 统计 (去重前):")
    print(f"  处理文件数: {processed_files}/{len(json_files)}")
    print(f"  提取摘要数: {total_summaries}")
    
    # 去重
    output_rows = filter_and_deduplicate_summaries(all_summaries)
    
    print(f"\n📊 统计 (去重后):")
    print(f"  保留摘要数: {len(output_rows)}")
    
    # 写入CSV文件
    try:
        with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.writer(csvfile)
            # 写入数据
            writer.writerows(output_rows)
        
        print(f"\n✅ 成功写入 CSV 文件: {OUTPUT_CSV}")
        print(f"   总行数: {len(output_rows)}")
    except Exception as e:
        print(f"\n❌ 写入CSV文件失败: {e}")


if __name__ == '__main__':
    main()
