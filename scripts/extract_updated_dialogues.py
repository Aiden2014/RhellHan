#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""提取新版游戏中新增或修改过的对话文本。"""

import csv
import re
import sys
from dataclasses import dataclass
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent

STEAM_BUILD_ID = "24107474"  # 在这里填写 Steam Build ID
OLD_DIALOGUE_FILTERED_CSV = Path(
    r"D:\SteamLibrary\steamapps\common\Rhell\BepInEx\plugins\resources\dialogue_filtered.csv"
)
NEW_DIALOGUE_CSV = PROJECT_ROOT / "resources" / "dialogue.csv"
SAFE_BUILD_ID_PATTERN = re.compile(r"^[A-Za-z0-9._-]+$")


class DialogueCsvError(ValueError):
    """表示输入 CSV 不符合对话文件格式。"""


@dataclass(frozen=True)
class ExtractionStats:
    old_rows: int
    new_rows: int
    unmatched_occurrences: int
    unique_rows: int


def build_output_path(project_root, build_id):
    if not build_id:
        raise ValueError("STEAM_BUILD_ID 不能为空，请填写 Steam Build ID")
    if not SAFE_BUILD_ID_PATTERN.fullmatch(build_id):
        raise ValueError("STEAM_BUILD_ID 只能包含字母、数字、点、下划线和连字符")
    return Path(project_root) / "resources" / f"dialogue_filtered_{build_id}.csv"


def select_updated_dialogues(old_rows, new_rows):
    """返回去重后的新版文本行，以及去重前的不匹配出现次数。"""
    old_texts = {row[1] for row in old_rows}
    seen_updated_texts = set()
    selected_rows = []
    unmatched_occurrences = 0

    for row in new_rows:
        dialogue = row[1]
        if dialogue in old_texts:
            continue

        unmatched_occurrences += 1
        if dialogue in seen_updated_texts:
            continue

        seen_updated_texts.add(dialogue)
        selected_rows.append([row[0], dialogue, ""])

    return selected_rows, unmatched_occurrences


def read_dialogue_rows(path):
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"输入文件不存在: {path}")

    rows = []
    with path.open("r", encoding="utf-8-sig", newline="") as csv_file:
        for line_number, row in enumerate(csv.reader(csv_file), start=1):
            if len(row) < 2:
                raise DialogueCsvError(
                    f"{path}:{line_number}: 对话 CSV 每行至少需要两列"
                )
            rows.append(row)
    return rows


def extract_updated_dialogues(old_path, new_path, output_path):
    old_rows = read_dialogue_rows(old_path)
    new_rows = read_dialogue_rows(new_path)
    selected_rows, unmatched_occurrences = select_updated_dialogues(
        old_rows, new_rows
    )

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8-sig", newline="") as csv_file:
        csv.writer(csv_file).writerows(selected_rows)

    return ExtractionStats(
        old_rows=len(old_rows),
        new_rows=len(new_rows),
        unmatched_occurrences=unmatched_occurrences,
        unique_rows=len(selected_rows),
    )


def main():
    try:
        output_path = build_output_path(PROJECT_ROOT, STEAM_BUILD_ID)
        stats = extract_updated_dialogues(
            OLD_DIALOGUE_FILTERED_CSV,
            NEW_DIALOGUE_CSV,
            output_path,
        )
    except (DialogueCsvError, FileNotFoundError, OSError, ValueError) as error:
        print(f"错误: {error}", file=sys.stderr)
        return 1

    print(f"旧版翻译行数: {stats.old_rows}")
    print(f"新版原始行数: {stats.new_rows}")
    print(f"新版不匹配出现次数: {stats.unmatched_occurrences}")
    print(f"去重后写入行数: {stats.unique_rows}")
    print(f"输出文件: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
