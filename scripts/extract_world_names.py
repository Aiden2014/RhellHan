import json
import csv
import os

INPUT_JSON = r"D:\SteamLibrary\steamapps\common\monobehaviour\WorldNames-level3-26001.json"
OUTPUT_CSV = r"d:\projects\RhellHan\resources\world_name.csv"

def extract_world_names():
    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
    
    try:
        with open(INPUT_JSON, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        world_area_names = data.get('worldAreaNames', {}).get('Array', [])
        
        extracted_data = []
        for index, name in enumerate(world_area_names):
            # For Unity JSON structured arrays, they might be list of dicts. We need to handle this.
            # Assuming it's a simple list of strings based on the prompt, or check if we need to extract from dict.
            # Let's check structure just in case.
            if isinstance(name, str):
                val = name
            elif isinstance(name, dict):
                # if unity serialized, might need to extract value
                val = list(name.values())[0] if name else ""
            else:
                val = str(name)
                
            formatted_first_column = f"{index}|||{val}"
            extracted_data.append([formatted_first_column, val])
            
        with open(OUTPUT_CSV, 'w', encoding='utf-8', newline='') as csvfile:
            writer = csv.writer(csvfile)
            for row in extracted_data:
                writer.writerow(row)
                
        print(f"Successfully extracted {len(extracted_data)} world names to {OUTPUT_CSV}")
            
    except Exception as e:
        print(f"Error processing {INPUT_JSON}: {e}")

if __name__ == "__main__":
    extract_world_names()