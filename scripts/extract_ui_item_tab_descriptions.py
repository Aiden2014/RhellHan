import json
import csv
import os
import glob

# Define directories
INPUT_DIR = r"D:\SteamLibrary\steamapps\common\monobehaviour"
OUTPUT_CSV = r"d:\projects\RhellHan\resources\item_tab_description.csv"

def extract_tab_descriptions():
    # Ensure the output directory exists
    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
    
    # File pattern to match
    pattern = os.path.join(INPUT_DIR, "UiItemTab-level1*.json")
    json_files = glob.glob(pattern)
    
    if not json_files:
        print(f"No files found matching: {pattern}")
        return

    extracted_data = []

    for file_path in json_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # Extract tabDescription
                if 'tabDescription' in data:
                    tab_description = data['tabDescription']
                    filename = os.path.basename(file_path)
                    
                    extracted_data.append([tab_description, tab_description])
        except Exception as e:
            print(f"Error processing {file_path}: {e}")

    # Write to CSV
    if extracted_data:
        # Sort by description to maintain order
        extracted_data.sort(key=lambda x: x[0])
        
        with open(OUTPUT_CSV, 'w', encoding='utf-8', newline='') as csvfile:
            writer = csv.writer(csvfile)
            for row in extracted_data:
                writer.writerow(row)
                
        print(f"Successfully extracted {len(extracted_data)} descriptions to {OUTPUT_CSV}")

if __name__ == "__main__":
    extract_tab_descriptions()
