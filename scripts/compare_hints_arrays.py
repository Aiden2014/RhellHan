#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
比对单个JSON文件中的 hints 和 demohints 数组的文本内容差异
"""

import json
import sys
from pathlib import Path


def load_json(filepath: str):
    """加载JSON文件"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ 无法读取 {filepath}: {e}")
        return None


def extract_hint_texts(data, key):
    """
    从JSON中提取指定键的hintText内容
    返回: {文本: 索引}
    """
    texts = {}
    
    if key not in data:
        print(f"⚠️  警告: 未找到键 '{key}'")
        return texts
    
    array_data = data[key]
    if not isinstance(array_data, dict) or 'Array' not in array_data:
        print(f"⚠️  警告: '{key}' 不是标准格式")
        return texts
    
    hint_array = array_data['Array']
    if not isinstance(hint_array, list):
        print(f"⚠️  警告: '{key}.Array' 不是列表")
        return texts
    
    for idx, hint_entry in enumerate(hint_array):
        if isinstance(hint_entry, dict) and 'hintText' in hint_entry:
            hint_text = hint_entry.get('hintText', '').strip()
            if hint_text:
                texts[hint_text] = idx
    
    return texts


def compare_hints_arrays(json_file: str, output_file: str = None):
    """
    比对JSON文件中的hints和demohints数组
    """
    print("=" * 80)
    print("Hints 和 DemoHints 数组内容比对")
    print("=" * 80)
    print(f"文件: {json_file}\n")
    
    # 加载文件
    data = load_json(json_file)
    if not data:
        return
    
    # 提取两个数组的文本内容
    hints_texts = extract_hint_texts(data, 'hints')
    demohints_texts = extract_hint_texts(data, 'demohints')
    
    print(f"📊 统计信息:")
    print(f"  hints 数组项数: {len(hints_texts)}")
    print(f"  demohints 数组项数: {len(demohints_texts)}\n")
    
    # 计算差异
    hints_only = set(hints_texts.keys()) - set(demohints_texts.keys())
    demohints_only = set(demohints_texts.keys()) - set(hints_texts.keys())
    common = set(hints_texts.keys()) & set(demohints_texts.keys())
    
    # 输出结果
    results = []
    
    if not hints_only and not demohints_only:
        msg = "✅ 两个数组的文本内容完全相同！"
        print(msg)
        results.append(msg)
    else:
        print(f"⚠️  找到差异:\n")
        results.append(f"⚠️  找到差异:\n")
        
        # hints中独有的
        if hints_only:
            msg = f"只在 hints 中出现的文本 ({len(hints_only)} 条):"
            print(msg)
            results.append(msg)
            for idx, text in enumerate(sorted(hints_only), 1):
                hint_idx = hints_texts[text]
                line = f"  {idx}. [索引 {hint_idx}] {text[:80]}"
                if len(text) > 80:
                    line += "..."
                print(line)
                results.append(line)
            print()
            results.append("")
        
        # demohints中独有的
        if demohints_only:
            msg = f"只在 demohints 中出现的文本 ({len(demohints_only)} 条):"
            print(msg)
            results.append(msg)
            for idx, text in enumerate(sorted(demohints_only), 1):
                hint_idx = demohints_texts[text]
                line = f"  {idx}. [索引 {hint_idx}] {text[:80]}"
                if len(text) > 80:
                    line += "..."
                print(line)
                results.append(line)
            print()
            results.append("")
    
    # 共同的文本
    msg = f"两个数组中都有的文本 ({len(common)} 条):"
    print(msg)
    results.append(msg)
    if common:
        for idx, text in enumerate(sorted(common), 1):
            line = f"  {idx}. {text[:80]}"
            if len(text) > 80:
                line += "..."
            print(line)
            results.append(line)
    else:
        print("  (无)")
        results.append("  (无)")
    
    # 保存到文件
    if output_file:
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("Hints 和 DemoHints 数组内容比对结果\n")
                f.write("=" * 80 + "\n")
                f.write(f"文件: {json_file}\n\n")
                f.write(f"统计信息:\n")
                f.write(f"  hints 数组项数: {len(hints_texts)}\n")
                f.write(f"  demohints 数组项数: {len(demohints_texts)}\n\n")
                
                for line in results:
                    f.write(line + "\n")
            
            print(f"\n✅ 结果已保存到: {output_file}")
        except Exception as e:
            print(f"\n❌ 无法保存结果: {e}")


def main():
    """主程序"""
    if len(sys.argv) < 2:
        print("用法: python compare_hints_arrays.py <JSON文件路径> [输出文件]")
        print("\n示例:")
        print('  python compare_hints_arrays.py "D:\\SteamLibrary\\steamapps\\common\\monobehaviour\\PauseBeesleHints-level1-28924.json"')
        print('  python compare_hints_arrays.py "path/to/file.json" "output/comparison.txt"')
        return
    
    json_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    # 验证文件存在
    if not Path(json_file).exists():
        print(f"❌ 文件不存在: {json_file}")
        return
    
    compare_hints_arrays(json_file, output_file)


if __name__ == '__main__':
    main()
