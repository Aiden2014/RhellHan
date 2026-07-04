#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从UiStoryPoint JSON文件中提取StoryText到CSV文件，并进行去重
"""

import json
import csv
import os
from pathlib import Path

from collections import defaultdict

# 路径配置
MONOBEHAVIOUR_FOLDER = r'D:\SteamLibrary\steamapps\common\monobehaviour'
RESOURCES_FOLDER = r'D:\projects\RhellHan\resources'
OUTPUT_CSV = os.path.join(RESOURCES_FOLDER, 'storypoint.csv')

def parse_handle_filename(filename):
    name_without_ext = filename.replace('.json', '')
    if not name_without_ext.startswith('UiStoryHandle-'):
        return None, None
    name_without_ext = name_without_ext[len('UiStoryHandle-'):]
    parts = name_without_ext.rsplit('-', 1)
    if len(parts) == 2:
        return parts[0], parts[1]
    return None, None

def read_story_text(json_path):
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            story_text = data.get('StoryText', '')
            if isinstance(story_text, str):
                return story_text
    except Exception:
        pass
    return ""

def process_data():
    array_groups = defaultdict(list)
    handle_files = sorted([f for f in Path(MONOBEHAVIOUR_FOLDER).glob('*.json') if f.name.startswith('UiStoryHandle-')])
    
    for handle_file in handle_files:
        level, handle_id = parse_handle_filename(handle_file.name)
        if not level or not handle_id:
            continue
            
        try:
            with open(handle_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception:
            continue
            
        story_points = data.get('storyPoints', {}).get('Array', [])
        if not isinstance(story_points, list):
            continue
            
        array_id = f"{level}|||{handle_id}"
        
        for idx, pt in enumerate(story_points):
            path_id = pt.get('m_PathID')
            if path_id is None:
                continue
                
            pt_filename = f"UiStoryPoint-{level}-{path_id}.json"
            pt_filepath = os.path.join(MONOBEHAVIOUR_FOLDER, pt_filename)
            
            if os.path.exists(pt_filepath):
                story_text = read_story_text(pt_filepath)
                if story_text.strip():
                    array_groups[array_id].append((idx, story_text.strip()))

    # 去重
    arrays = list(array_groups.keys())
    merged = set()
    output_rows = []
    
    for i, array_id1 in enumerate(arrays):
        if array_id1 in merged:
            continue
            
        group1 = sorted(array_groups[array_id1], key=lambda x: x[0])
        texts1 = [t for _, t in group1]
        
        if not texts1:
            continue
            
        duplicate_arrays = [array_id1]
        
        for j in range(i + 1, len(arrays)):
            array_id2 = arrays[j]
            if array_id2 in merged:
                continue
            
            group2 = sorted(array_groups[array_id2], key=lambda x: x[0])
            texts2 = [t for _, t in group2]
            
            # 判断两个数组的内容和顺序完全相同
            if len(texts1) == len(texts2) and texts1 == texts2:
                duplicate_arrays.append(array_id2)
                merged.add(array_id2)
                
        # 保留第一个找到的数组
        level, handle_id = array_id1.split('|||')
        for idx, text in group1:
            # 格式: id|||storyPoints索引|||storypoint内容
            first_col = f"{handle_id}|||{idx}|||{text}"
            output_rows.append([first_col, text, ''])
            
        merged.add(array_id1)
        
    return output_rows

def main():
    print("=" * 70)
    print("从 UiStoryHandle 提取关联的 UiStoryPoint StoryText 并按数组去重")
    print("=" * 70)
    
    if not os.path.isdir(MONOBEHAVIOUR_FOLDER):
        print(f"❌ 错误: 文件夹不存在: {MONOBEHAVIOUR_FOLDER}")
        return
    
    os.makedirs(RESOURCES_FOLDER, exist_ok=True)
    
    output_rows = process_data()
    
    print(f"\n📊 统计:")
    print(f"  合并后保留的独立UiStoryPoint条数: {len(output_rows)}")
    
    # 写入CSV
    try:
        with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(output_rows)
        print(f"\n✅ 成功写入 CSV 文件: {OUTPUT_CSV}")
    except Exception as e:
        print(f"\n❌ 写入CSV文件失败: {e}")

if __name__ == '__main__':
    main()
