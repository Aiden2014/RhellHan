#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从 UiStoryHandle JSON 文件中提取 endPoint 和 summaryPoint 的 StoryText，
分别写入 endpoint.csv 和 summarypoint.csv
"""

import json
import csv
import os
from pathlib import Path

MONOBEHAVIOUR_FOLDER = r'D:\SteamLibrary\steamapps\common\monobehaviour'
RESOURCES_FOLDER = r'D:\projects\RhellHan\resources'
ENDPOINT_CSV = os.path.join(RESOURCES_FOLDER, 'endpoint.csv')
SUMMARYPOINT_CSV = os.path.join(RESOURCES_FOLDER, 'summarypoint.csv')


def parse_handle_filename(filename):
    name_without_ext = filename.replace('.json', '')
    if not name_without_ext.startswith('UiStoryHandle-'):
        return None, None
    name_without_ext = name_without_ext[len('UiStoryHandle-'):]
    parts = name_without_ext.rsplit('-', 1)
    if len(parts) == 2:
        return parts[0], parts[1]
    return None, None


def read_story_text(json_path):
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        text = data.get('StoryText', '')
        if isinstance(text, str) and text.strip():
            return text.strip()
    except Exception:
        pass
    return ""


def process_data():
    endpoints = []
    summarypoints = []
    handle_files = sorted(Path(MONOBEHAVIOUR_FOLDER).glob('UiStoryHandle-level1-*.json'))

    for handle_file in handle_files:
        level, handle_id = parse_handle_filename(handle_file.name)
        if not level or not handle_id:
            continue

        try:
            with open(handle_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception:
            continue

        end_path_id = (data.get('endPoint') or {}).get('m_PathID', 0)
        summary_path_id = (data.get('summaryPoint') or {}).get('m_PathID', 0)

        if end_path_id:
            pt_filename = f"UiStoryPoint-{level}-{end_path_id}.json"
            pt_filepath = os.path.join(MONOBEHAVIOUR_FOLDER, pt_filename)
            story_text = read_story_text(pt_filepath)
            if story_text:
                first_col = f"{handle_id}|||endPoint"
                endpoints.append([first_col, story_text, ''])

        if summary_path_id:
            pt_filename = f"UiStoryPoint-{level}-{summary_path_id}.json"
            pt_filepath = os.path.join(MONOBEHAVIOUR_FOLDER, pt_filename)
            story_text = read_story_text(pt_filepath)
            if story_text:
                first_col = f"{handle_id}|||summaryPoint"
                summarypoints.append([first_col, story_text, ''])

    return endpoints, summarypoints


def main():
    print("=" * 70)
    print("从 UiStoryHandle 提取 endPoint 和 summaryPoint")
    print("=" * 70)

    if not os.path.isdir(MONOBEHAVIOUR_FOLDER):
        print(f"错误: 文件夹不存在: {MONOBEHAVIOUR_FOLDER}")
        return

    os.makedirs(RESOURCES_FOLDER, exist_ok=True)

    endpoints, summarypoints = process_data()

    print(f"\nendPoint: {len(endpoints)} 条")
    print(f"summaryPoint: {len(summarypoints)} 条")

    with open(ENDPOINT_CSV, 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(endpoints)
    print(f"\n已写入: {ENDPOINT_CSV}")

    with open(SUMMARYPOINT_CSV, 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(summarypoints)
    print(f"已写入: {SUMMARYPOINT_CSV}")


if __name__ == '__main__':
    main()
