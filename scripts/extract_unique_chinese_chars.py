#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
extract all unique Chinese characters from specified CSV files
"""

import csv
import re
from pathlib import Path

def extract_unique_chinese_chars(csv_files, output_file):
    """
    Extract all unique Chinese characters from specified CSV files
    
    Args:
        csv_files: List of CSV file paths
        output_file: Output file path
    """
    # Use a set to store unique Chinese characters
    chinese_chars = set()
    
    # Read CSV files
    for csv_file in csv_files:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            
            for row in reader:
                # Iterate through each column
                for cell in row:
                    # Extract all Chinese characters in the cell
                    for char in cell:
                        chinese_chars.add(char)
    
    # Sort by Unicode order
    sorted_chars = sorted(chinese_chars)
    
    # Write to output file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(''.join(sorted_chars))
    
    print(f"Successfully extracted {len(sorted_chars)} unique Chinese characters")
    print(f"Saved to: {output_file}")


def main():
    # Set file paths
    project_root = Path(__file__).parent.parent
    resources_dir = project_root / 'resources'
    csv_files = sorted(resources_dir.glob('*.csv'))
    output_file = resources_dir / 'unique_chinese_chars.txt'

    if not csv_files:
        print(f"Error: No CSV files found in {resources_dir}")
        return
    
    # Extract Chinese characters
    extract_unique_chinese_chars(csv_files, output_file)

if __name__ == '__main__':
    main()
