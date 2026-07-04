import csv
from collections import defaultdict

def parse_first_column(first_col):
    """
    解析第一列，提取数组标识 (array_id) 和索引 (index)
    例如: level1|||23912|||0|||... -> (level1|||23912, 0)
    """
    parts = first_col.split('|||')
    if len(parts) >= 3:
        array_id = '|||'.join(parts[:2])  # level1|||23912
        try:
            index = int(parts[2])
            return array_id, index
        except ValueError:
            return None, None
    return None, None

def filter_and_deduplicate_dialogues(input_file, output_file):
    output_rows = []
    array_groups = defaultdict(list)  # array_id -> [(index, row, dialogue, translation), ...]

    # 第一步：读取文件，按数组分组
    with open(input_file, 'r', encoding='utf-8') as infile:
        reader = csv.reader(infile)
        for row in reader:
            if len(row) < 2:
                continue
            
            array_id, index = parse_first_column(row[0])
            if array_id is None:
                continue
            
            dialogue = row[1] if len(row) > 1 else ""
            translation = row[2] if len(row) > 2 else ""
            
            array_groups[array_id].append((index, row, dialogue, translation.strip()))

    # 第二步：比较数组，找出内容相同的数组对
    arrays = list(array_groups.keys())
    merged = set()  # 记录已经处理过的数组
    
    for i, array_id1 in enumerate(arrays):
        if array_id1 in merged:
            continue
        
        group1 = sorted(array_groups[array_id1], key=lambda x: x[0])
        dialogues1 = [d for _, _, d, _ in group1]
        translations1 = [t for _, _, _, t in group1]
        trans_count1 = sum(1 for t in translations1 if t)
        
        # 与其他数组比较，找出dialogue内容完全相同的
        duplicate_arrays = [array_id1]  # 包括自己
        
        for j in range(i + 1, len(arrays)):
            array_id2 = arrays[j]
            if array_id2 in merged:
                continue
            
            group2 = sorted(array_groups[array_id2], key=lambda x: x[0])
            dialogues2 = [d for _, _, d, _ in group2]
            
            # 检查dialogue内容和顺序是否完全相同
            if len(dialogues1) == len(dialogues2) and dialogues1 == dialogues2:
                duplicate_arrays.append(array_id2)
                merged.add(array_id2)
        
        # 如果有重复数组，保留翻译最多的
        if len(duplicate_arrays) > 1:
            best_array_id = None
            best_trans_count = -1
            
            for dup_id in duplicate_arrays:
                group = sorted(array_groups[dup_id], key=lambda x: x[0])
                trans_count = sum(1 for _, _, _, t in group if t)
                if trans_count > best_trans_count:
                    best_trans_count = trans_count
                    best_array_id = dup_id
            
            # 只保留翻译最多的数组的所有行
            group = sorted(array_groups[best_array_id], key=lambda x: x[0])
            for _, row, _, _ in group:
                output_rows.append(row)
        else:
            # 没有重复，直接加入此数组的所有行
            group = sorted(array_groups[array_id1], key=lambda x: x[0])
            for _, row, _, _ in group:
                output_rows.append(row)
        
        merged.add(array_id1)

    with open(output_file, 'w', encoding='utf-8', newline='') as outfile:
        writer = csv.writer(outfile)
        writer.writerows(output_rows)

if __name__ == "__main__":
    input_csv = "./resources/dialogue.csv"
    output_csv = "./resources/dialogue_filtered.csv"
    filter_and_deduplicate_dialogues(input_csv, output_csv)
    print(f"Filtered and deduplicated dialogues saved to {output_csv}")