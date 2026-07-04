#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
比对两个JSON文件的差异
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple


def load_json(filepath: str) -> Dict[str, Any]:
    """加载JSON文件"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ 无法读取 {filepath}: {e}")
        return {}


def compare_dicts(dict1: Dict, dict2: Dict, path: str = "") -> List[str]:
    """
    递归比对两个字典的差异
    返回差异列表
    """
    differences = []
    
    # 检查字典1中的所有key
    for key in dict1.keys():
        current_path = f"{path}.{key}" if path else key
        
        if key not in dict2:
            differences.append(f"❌ 键缺失: {current_path} (仅在第一个文件中存在)")
        else:
            val1 = dict1[key]
            val2 = dict2[key]
            
            # 递归比对嵌套dict
            if isinstance(val1, dict) and isinstance(val2, dict):
                differences.extend(compare_dicts(val1, val2, current_path))
            # 比对列表
            elif isinstance(val1, list) and isinstance(val2, list):
                differences.extend(compare_lists(val1, val2, current_path))
            # 比对基本值
            elif val1 != val2:
                differences.append(f"⚠️  值不同: {current_path}")
                differences.append(f"   文件1: {repr(val1)[:100]}")
                differences.append(f"   文件2: {repr(val2)[:100]}")
    
    # 检查字典2中是否有字典1没有的key
    for key in dict2.keys():
        if key not in dict1:
            current_path = f"{path}.{key}" if path else key
            differences.append(f"❌ 键缺失: {current_path} (仅在第二个文件中存在)")
    
    return differences


def compare_lists(list1: List, list2: List, path: str = "") -> List[str]:
    """
    比对两个列表的差异
    """
    differences = []
    
    if len(list1) != len(list2):
        differences.append(f"⚠️  列表长度不同: {path}")
        differences.append(f"   文件1: {len(list1)} 项")
        differences.append(f"   文件2: {len(list2)} 项")
    
    # 比对相同长度范围内的元素
    for idx in range(min(len(list1), len(list2))):
        current_path = f"{path}[{idx}]"
        item1 = list1[idx]
        item2 = list2[idx]
        
        if isinstance(item1, dict) and isinstance(item2, dict):
            differences.extend(compare_dicts(item1, item2, current_path))
        elif isinstance(item1, list) and isinstance(item2, list):
            differences.extend(compare_lists(item1, item2, current_path))
        elif item1 != item2:
            differences.append(f"⚠️  元素不同: {current_path}")
            differences.append(f"   文件1: {repr(item1)[:100]}")
            differences.append(f"   文件2: {repr(item2)[:100]}")
    
    return differences


def compare_json_files(file1: str, file2: str, output_file: str = None):
    """
    比对两个JSON文件
    """
    print("=" * 70)
    print("JSON 文件差异比对工具")
    print("=" * 70)
    print(f"文件1: {file1}")
    print(f"文件2: {file2}\n")
    
    # 加载文件
    json1 = load_json(file1)
    json2 = load_json(file2)
    
    if not json1 or not json2:
        print("❌ 无法加载JSON文件")
        return
    
    # 比对差异
    differences = compare_dicts(json1, json2)
    
    # 输出结果
    if not differences:
        print("✅ 两个文件完全相同！")
    else:
        print(f"找到 {len(differences)} 条差异:\n")
        for diff in differences:
            print(diff)
    
    # 保存到文件
    if output_file:
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("JSON 文件差异比对结果\n")
                f.write("=" * 70 + "\n")
                f.write(f"文件1: {file1}\n")
                f.write(f"文件2: {file2}\n\n")
                
                if not differences:
                    f.write("✅ 两个文件完全相同！\n")
                else:
                    f.write(f"找到 {len(differences)} 条差异:\n\n")
                    for diff in differences:
                        f.write(diff + "\n")
            
            print(f"\n✅ 结果已保存到: {output_file}")
        except Exception as e:
            print(f"\n❌ 无法保存结果: {e}")


def main():
    """主程序"""
    if len(sys.argv) < 3:
        print("用法: python compare_json_files.py <文件1> <文件2> [输出文件]")
        print("\n示例:")
        print("  python compare_json_files.py file1.json file2.json")
        print("  python compare_json_files.py file1.json file2.json diff.txt")
        return
    
    file1 = sys.argv[1]
    file2 = sys.argv[2]
    output_file = sys.argv[3] if len(sys.argv) > 3 else None
    
    # 验证文件存在
    if not Path(file1).exists():
        print(f"❌ 文件不存在: {file1}")
        return
    
    if not Path(file2).exists():
        print(f"❌ 文件不存在: {file2}")
        return
    
    compare_json_files(file1, file2, output_file)


if __name__ == '__main__':
    main()
