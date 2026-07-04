#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从monobehaviour JSON文件中提取hints到CSV文件
"""

import json
import csv
import os
import sys
from pathlib import Path


def parse_filename(filename):
    """
    解析JSON文件名，提取组件
    格式: {前缀}-{中间部分}-{后缀}.json
    例如: PauseBeesleHints-level1-28924.json
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


def extract_hints_from_file(json_file):
    """
    从单个JSON文件中提取hints、demohints和finishedRandomHints
    返回: [(id_string, hint_text), ...]
    """
    results = []
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"⚠️  无法读取 {os.path.basename(json_file)}: {e}")
        return results
    
    filename = os.path.basename(json_file)
    prefix, middle, suffix = parse_filename(filename)
    
    if prefix is None or middle is None or suffix is None:
        print(f"⚠️  无法解析文件名格式: {filename}")
        return results
    
    # 提取 hints、demohints和finishedRandomHints三个数组
    for array_type in ['hints', 'demohints', 'finishedRandomHints']:
        array_data = data.get(array_type, {})
        if not isinstance(array_data, dict):
            continue
        
        array_content = array_data.get('Array', [])
        if not isinstance(array_content, list):
            continue
        
        # 提取每个hint
        for idx, hint_entry in enumerate(array_content):
            if isinstance(hint_entry, dict) and 'hintText' in hint_entry:
                hint_text = hint_entry.get('hintText', '')
                if isinstance(hint_text, str) and hint_text.strip():
                    # 第一列格式: hint、demohint、finishedRandomHints|||idx|||hint_text
                    id_string = f"{array_type}|||{idx}|||{hint_text}"
                    results.append((id_string, hint_text))
    
    return results


def main():
    """
    主程序
    """
    # 处理命令行参数
    if len(sys.argv) < 2:
        print("用法: python extract_hints_from_monobehaviour.py <JSON文件路径> [输出CSV路径]")
        print("\n示例:")
        print('  python extract_hints_from_monobehaviour.py "D:\\SteamLibrary\\steamapps\\common\\monobehaviour\\PauseBeesleHints-level1-28924.json"')
        print('  python extract_hints_from_monobehaviour.py "path/to/file.json" "output/hints.csv"')
        return
    
    json_file = sys.argv[1]
    output_csv = sys.argv[2] if len(sys.argv) > 2 else r'D:\projects\RhellHan\resources\hint.csv'
    
    print("=" * 70)
    print("从 MonoBehaviour JSON 提取 Hints")
    print("=" * 70)
    print(f"源文件: {json_file}")
    print(f"输出文件: {output_csv}\n")
    
    # 验证文件存在
    if not os.path.exists(json_file):
        print(f"❌ 错误: 文件不存在: {json_file}")
        return
    
    # 创建输出目录
    output_dir = os.path.dirname(output_csv)
    if output_dir and not os.path.isdir(output_dir):
        print(f"⚠️  创建输出文件夹: {output_dir}")
        os.makedirs(output_dir, exist_ok=True)
    
    # 提取数据
    hints = extract_hints_from_file(json_file)
    
    if not hints:
        print(f"❌ 没有提取到任何提示")
        return
    
    print(f"✓ {os.path.basename(json_file)}: {len(hints)} 条提示\n")
    
    # 写入CSV文件
    try:
        with open(output_csv, 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.writer(csvfile)
            # 写入数据
            for id_string, hint_text in hints:
                writer.writerow([id_string, hint_text, ''])
        
        print(f"✅ 成功写入 CSV 文件: {output_csv}")
        print(f"   总行数: {len(hints)} (不含表头)")
    except Exception as e:
        print(f"❌ 写入CSV文件失败: {e}")


if __name__ == '__main__':
    main()
