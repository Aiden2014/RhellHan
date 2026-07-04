#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从monobehaviour JSON文件中提取dialogues到CSV文件
"""

import json
import csv
import os
from pathlib import Path

# 路径配置
MONOBEHAVIOUR_FOLDER = r'D:\SteamLibrary\steamapps\common\monobehaviour'
RESOURCES_FOLDER = r'D:\projects\RhellHan\resources'
OUTPUT_CSV = os.path.join(RESOURCES_FOLDER, 'dialogue_option.csv')
FILTERED_CSV = os.path.join(RESOURCES_FOLDER, 'dialogue_filtered.csv')


def parse_filename(filename):
    """
    解析JSON文件名，提取组件
    格式: {前缀}-{中间部分}-{后缀}.json
    例如: InteractDialogue-level3-21478.json
    返回: (前缀, 中间部分, 后缀)
    """
    # 移除 .json 扩展名
    name_without_ext = filename.replace('.json', '')
    
    # 按 '-' 分割
    parts = name_without_ext.split('-')
    
    if len(parts) >= 3:
        prefix = parts[0]
        middle = '-'.join(parts[1:-1])  # 处理中间可能有多个 '-' 的情况
        suffix = parts[-1]
        return prefix, middle, suffix
    
    return None, None, None


def extract_dialogues_from_file(json_file, idx0_text=""):
    """
    从单个JSON文件中提取dialogueOptions
    返回: [(id_string, dialogue_text), ...]
    """
    results = []
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"⚠️  无法读取 {os.path.basename(json_file)}: {e}")
        return results
    
    # 获取 dialogueOptionsdialogues 数组
    dialogueOptions = data.get('dialogueOptions', {})
    if not isinstance(dialogueOptions, dict):
        return results
    
    dialogue_array = dialogueOptions.get('Array', [])
    if not isinstance(dialogue_array, list):
        return results
    
    filename = os.path.basename(json_file)
    prefix, middle, suffix = parse_filename(filename)
    
    if prefix is None or middle is None or suffix is None:
        print(f"⚠️  无法解析文件名格式: {filename}")
        return results
    
    # 提取每个optionText
    for idx, dialogue_entry in enumerate(dialogue_array):
        if isinstance(dialogue_entry, dict) and 'optionText' in dialogue_entry:
            dialogue_text = dialogue_entry.get('optionText', '')
            if isinstance(dialogue_text, str) and dialogue_text.strip():
                # 第一列格式: middle|||suffix|||idx0_text|||idx|||dialogue_text
                id_string = f"{middle}|||{suffix}|||{idx0_text}|||{idx}|||{dialogue_text}"
                results.append((id_string, dialogue_text))
    
    return results


def main():
    """
    主程序
    """
    print("=" * 70)
    print("从 MonoBehaviour JSON 提取 Dialogue Options")
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
    
    # 从 dialogue_filtered.csv 提取目标 JSON 文件的 component 标识和索引0的内容
    target_identifiers = set()
    target_idx0_text = {}
    try:
        with open(FILTERED_CSV, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            for row in reader:
                if not row:
                    continue
                id_string = row[0]
                parts = id_string.split('|||')
                if len(parts) >= 4:
                    middle, suffix, idx, text = parts[0], parts[1], parts[2], parts[3]
                    # 存储 (middle, suffix) 作为匹配依据
                    target_identifiers.add((middle, suffix))
                    
                    if idx == '0' and (middle, suffix) not in target_idx0_text:
                        target_idx0_text[(middle, suffix)] = text
    except Exception as e:
        print(f"❌ 读取 {FILTERED_CSV} 失败: {e}")
        return
        
    if not target_identifiers:
        print(f"❌ 未能从 {FILTERED_CSV} 提取到任何有效标识")
        return

    # 收集并过滤匹配的JSON文件
    all_json_files = sorted(Path(MONOBEHAVIOUR_FOLDER).glob('*.json'))
    json_files = []
    
    for jf in all_json_files:
        prefix, middle, suffix = parse_filename(jf.name)
        if (middle, suffix) in target_identifiers:
            json_files.append(jf)
            
    print(f"从 CSV 识别出 {len(target_identifiers)} 个目标组件，匹配到 {len(json_files)} 个对应的 JSON 文件\n")
    
    if not json_files:
        print("❌ 没有找到匹配的JSON文件")
        return
    
    # 提取数据
    all_dialogues = []
    processed_files = 0
    total_dialogues = 0
    
    for json_file in json_files:
        prefix, middle, suffix = parse_filename(json_file.name)
        idx0_text = target_idx0_text.get((middle, suffix), "")
        dialogues = extract_dialogues_from_file(str(json_file), idx0_text)
        if dialogues:
            all_dialogues.extend(dialogues)
            processed_files += 1
            total_dialogues += len(dialogues)
            print(f"✓ {json_file.name}: {len(dialogues)} 条对话")
    
    print(f"\n📊 统计:")
    print(f"  处理文件数: {processed_files}/{len(json_files)}")
    print(f"  提取对话数: {total_dialogues}")
    
    # 写入CSV文件
    try:
        with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.writer(csvfile)
            # 写入数据
            for id_string, dialogue_text in all_dialogues:
                writer.writerow([id_string, dialogue_text, ''])
        
        print(f"\n✅ 成功写入 CSV 文件: {OUTPUT_CSV}")
        print(f"   总行数: {len(all_dialogues)} (不含表头)")
    except Exception as e:
        print(f"\n❌ 写入CSV文件失败: {e}")


if __name__ == '__main__':
    main()
