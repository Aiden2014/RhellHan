import json
import os
import csv
from pathlib import Path

# 定义源目录和输出路径
source_dir = r"D:\SteamLibrary\steamapps\common\monobehaviour"
output_file = r"d:\projects\RhellHan\resources\room_hint.csv"

def extract_dialogues(obj, dialogues_list):
    """
    递归地从JSON对象中提取所有的dialogue值
    """
    if isinstance(obj, dict):
        # 如果找到dialogue键，添加其值
        if "dialogue" in obj:
            dialogues_list.append(obj["dialogue"])
        
        # 递归遍历所有值
        for value in obj.values():
            extract_dialogues(value, dialogues_list)
    
    elif isinstance(obj, list):
        # 递归遍历列表中的所有元素
        for item in obj:
            extract_dialogues(item, dialogues_list)

def main():
    all_dialogues = []
    
    # 检查源目录是否存在
    if not os.path.exists(source_dir):
        print(f"错误: 目录不存在 {source_dir}")
        return
    
    # 查找所有RoomHint-开头的JSON文件
    json_files = [f for f in os.listdir(source_dir) if f.startswith("RoomHint-") and f.endswith(".json")]
    
    if not json_files:
        print(f"警告: 在 {source_dir} 中未找到RoomHint-*.json文件")
    
    print(f"找到 {len(json_files)} 个JSON文件")
    
    # 处理每个JSON文件
    for filename in json_files:
        filepath = os.path.join(source_dir, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 提取这个文件中的所有dialogue值
            extract_dialogues(data, all_dialogues)
            print(f"✓ 处理: {filename}")
        
        except json.JSONDecodeError as e:
            print(f"✗ JSON解析错误 {filename}: {e}")
        except Exception as e:
            print(f"✗ 错误处理 {filename}: {e}")
    
    # 创建输出目录（如果不存在）
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # 去重（保留顺序）
    seen = set()
    unique_dialogues = []
    for dialogue in all_dialogues:
        if dialogue not in seen:
            seen.add(dialogue)
            unique_dialogues.append(dialogue)
    
    # 将dialogue值写入CSV文件（两列相同的值）
    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            for dialogue in unique_dialogues:
                writer.writerow([dialogue, dialogue])
        
        print(f"\n✓ 成功! 提取了 {len(all_dialogues)} 条dialogue，去重后 {len(unique_dialogues)} 条")
        print(f"✓ 已保存到: {output_file}")
    
    except Exception as e:
        print(f"✗ 写入文件时出错: {e}")

if __name__ == "__main__":
    main()
