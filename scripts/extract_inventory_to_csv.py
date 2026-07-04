import json
import csv
import os

# 读取JSON文件
json_file = r"D:\SteamLibrary\steamapps\common\monobehaviour\PlayerInventory-level1-25760.json"
output_dir = r"d:\projects\RhellHan\resources"

print(f"读取JSON文件: {json_file}")

with open(json_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

# 处理ItemIndex
if "ItemIndex" in data and "Array" in data["ItemIndex"]:
    items = data["ItemIndex"]["Array"]
    print(f"找到 {len(items)} 个物品条目")
    
    # 第一个CSV：ItemIndex Name (第一列: Index|||Name, 第二列: Name)
    with open(os.path.join(output_dir, "item_name.csv"), 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        for idx, item in enumerate(items):
            name = item.get("Name", "")
            writer.writerow([f"{idx}|||{name}", name])
    print(f"✓ item_name.csv 已生成")
    
    # 第二个CSV：ItemIndex Description (第一列: Index|||Name|||Description, 第二列: Description)
    with open(os.path.join(output_dir, "item_description.csv"), 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        for idx, item in enumerate(items):
            name = item.get("Name", "")
            description = item.get("Description", "")
            writer.writerow([f"{idx}|||{name}|||{description}", description])
    print(f"✓ item_descriptions.csv 已生成")
else:
    print("⚠ 未找到ItemIndex数据")

# 处理RuneIndex
if "RuneIndex" in data and "Array" in data["RuneIndex"]:
    runes = data["RuneIndex"]["Array"]
    print(f"找到 {len(runes)} 个符文条目")
    
    # 第三个CSV：RuneIndex Name (第一列: Index|||Name, 第二列: Name)
    with open(os.path.join(output_dir, "rune_name.csv"), 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        for idx, rune in enumerate(runes):
            name = rune.get("Name", "")
            writer.writerow([f"{idx}|||{name}", name])
    print(f"✓ rune_name.csv 已生成")
    
    # 第四个CSV：RuneIndex Description (第一列: Index|||Name|||Description, 第二列: Description)
    with open(os.path.join(output_dir, "rune_description.csv"), 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        for idx, rune in enumerate(runes):
            name = rune.get("Name", "")
            description = rune.get("Description", "")
            writer.writerow([f"{idx}|||{name}|||{description}", description])
    print(f"✓ rune_description.csv 已生成")
else:
    print("⚠ 未找到RuneIndex数据")

print("提取完成！")
