# Dialogue Update Extractor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a Python script that extracts unique new or corrected dialogue text from the latest raw CSV into a Steam-build-specific translation CSV.

**Architecture:** Keep exact text comparison in a pure function, place validated CSV reading and writing in a separate orchestration function, and keep repository paths plus Steam Build ID handling at the command-line boundary. This makes matching behavior testable with in-memory rows and file safety testable with temporary files.

**Tech Stack:** Python 3 standard library (`csv`, `dataclasses`, `pathlib`, `re`, `sys`, `unittest`, `tempfile`).

## Global Constraints

- Do not add third-party dependencies.
- Read and write dialogue CSV files with `utf-8-sig` and `newline=""`.
- Compare the second column exactly, including case, punctuation, Unicode characters, and surrounding whitespace.
- Deduplicate selected rows by exact English text and retain the first new-file occurrence.
- Write exactly three columns with an empty translation field and no header.
- Resolve new input and output paths from the repository, not the process working directory.
- Leave `STEAM_BUILD_ID = ""` for the maintainer to fill in.
- Execute Python scripts and test commands with the Windows launcher form `py ...`.
- Do not modify `resources/dialogue.csv` or the previous translated CSV.
- Use Conventional Commit messages in `type(scope): subject` form.

---

### Task 1: Exact text selection and deduplication

**Files:**
- Create: `scripts/extract_updated_dialogues.py`
- Create: `tests/test_extract_updated_dialogues.py`

**Interfaces:**
- Consumes: Old and new CSV rows as `list[list[str]]`.
- Produces: `select_updated_dialogues(old_rows, new_rows) -> tuple[list[list[str]], int]`, where the integer is the number of unmatched raw occurrences before deduplication.

- [ ] **Step 1: Write failing behavior tests**

Create `tests/test_extract_updated_dialogues.py` with literal expectations that independently cover old-text exclusion, corrected-text selection, first-occurrence deduplication, and exact whitespace comparison:

```python
import importlib
import unittest


def require_feature(name):
    try:
        module = importlib.import_module("scripts.extract_updated_dialogues")
        return getattr(module, name)
    except (ModuleNotFoundError, AttributeError) as error:
        raise AssertionError(f"缺少待实现功能: {name}") from error


def select_updated_dialogues(*args):
    return require_feature("select_updated_dialogues")(*args)


class SelectUpdatedDialoguesTests(unittest.TestCase):
    def test_excludes_text_already_present_in_old_rows(self):
        old_rows = [["old|||1|||0|||Same", "Same", "相同"]]
        new_rows = [["new|||2|||0|||Same", "Same", ""]]

        selected, unmatched = select_updated_dialogues(old_rows, new_rows)

        self.assertEqual([], selected)
        self.assertEqual(0, unmatched)

    def test_selects_corrected_text_and_clears_translation(self):
        old_rows = [["old|||1|||0|||Their resting", "Their resting", "旧译"]]
        new_rows = [["new|||2|||0|||They're resting", "They're resting", "ignored"]]

        selected, unmatched = select_updated_dialogues(old_rows, new_rows)

        self.assertEqual(
            [["new|||2|||0|||They're resting", "They're resting", ""]],
            selected,
        )
        self.assertEqual(1, unmatched)

    def test_deduplicates_changed_text_using_first_new_row(self):
        new_rows = [
            ["level1|||10|||0|||Changed", "Changed", ""],
            ["level2|||20|||4|||Changed", "Changed", ""],
        ]

        selected, unmatched = select_updated_dialogues([], new_rows)

        self.assertEqual(
            [["level1|||10|||0|||Changed", "Changed", ""]],
            selected,
        )
        self.assertEqual(2, unmatched)

    def test_treats_trailing_space_as_an_exact_text_change(self):
        old_rows = [["old", "Keep space ", "旧译"]]
        new_rows = [["new", "Keep space", ""]]

        selected, unmatched = select_updated_dialogues(old_rows, new_rows)

        self.assertEqual([["new", "Keep space", ""]], selected)
        self.assertEqual(1, unmatched)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the tests and verify RED**

Run:

```powershell
py -m unittest discover -s tests -p "test_extract_updated_dialogues.py" -v
```

Expected: four assertion failures containing `缺少待实现功能: select_updated_dialogues` because the production module does not exist. The RED run must contain failures, not import errors.

- [ ] **Step 3: Implement the minimal pure selection function**

Create `scripts/extract_updated_dialogues.py` with:

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""提取新版游戏中新增或修改过的对话文本。"""


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
```

- [ ] **Step 4: Run the tests and verify GREEN**

Run the same unittest discovery command. Expected: four tests pass with no warnings or errors.

- [ ] **Step 5: Commit the independently working selection behavior**

```powershell
git add -- scripts/extract_updated_dialogues.py tests/test_extract_updated_dialogues.py
git commit -m "feat(scripts): select unique updated dialogue text"
```

### Task 2: Validated CSV extraction

**Files:**
- Modify: `scripts/extract_updated_dialogues.py`
- Modify: `tests/test_extract_updated_dialogues.py`

**Interfaces:**
- Consumes: `old_path`, `new_path`, and `output_path` as `pathlib.Path` values.
- Produces: `ExtractionStats(old_rows, new_rows, unmatched_occurrences, unique_rows)` and a three-column CSV at `output_path`.
- Raises: `FileNotFoundError` for missing inputs and `DialogueCsvError` for a row with fewer than two columns.

- [ ] **Step 1: Add failing file-boundary tests**

Extend the test imports and add a test class using real temporary files:

```python
import csv
import tempfile
from pathlib import Path

def extract_updated_dialogues(*args):
    return require_feature("extract_updated_dialogues")(*args)


class CsvExtractionTests(unittest.TestCase):
    def write_csv(self, path, rows):
        with path.open("w", encoding="utf-8-sig", newline="") as csv_file:
            csv.writer(csv_file).writerows(rows)

    def test_writes_utf8_bom_and_exactly_three_output_columns(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            old_path = root / "old.csv"
            new_path = root / "new.csv"
            output_path = root / "output.csv"
            self.write_csv(old_path, [["old", "Known", "已译"]])
            self.write_csv(
                new_path,
                [
                    ["new1", "Known", ""],
                    ["new2", "Corrected", "source value", "extra"],
                ],
            )

            stats = extract_updated_dialogues(old_path, new_path, output_path)

            self.assertTrue(output_path.read_bytes().startswith(b"\xef\xbb\xbf"))
            with output_path.open(encoding="utf-8-sig", newline="") as csv_file:
                self.assertEqual([["new2", "Corrected", ""]], list(csv.reader(csv_file)))
            self.assertEqual(1, stats.old_rows)
            self.assertEqual(2, stats.new_rows)
            self.assertEqual(1, stats.unmatched_occurrences)
            self.assertEqual(1, stats.unique_rows)

    def test_malformed_input_does_not_replace_existing_output(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            old_path = root / "old.csv"
            new_path = root / "new.csv"
            output_path = root / "output.csv"
            self.write_csv(old_path, [["old", "Known", "已译"]])
            self.write_csv(new_path, [["only one column"]])
            output_path.write_text("keep me", encoding="utf-8")

            error_type = require_feature("DialogueCsvError")
            with self.assertRaisesRegex(error_type, "new.csv:1"):
                extract_updated_dialogues(old_path, new_path, output_path)

            self.assertEqual("keep me", output_path.read_text(encoding="utf-8"))

    def test_missing_input_does_not_create_output(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            output_path = root / "output.csv"

            with self.assertRaises(FileNotFoundError):
                extract_updated_dialogues(root / "missing-old.csv", root / "missing-new.csv", output_path)

            self.assertFalse(output_path.exists())
```

- [ ] **Step 2: Run the tests and verify RED**

Run the unittest discovery command. Expected: the four Task 1 tests pass and the three new tests fail with assertions naming the missing `extract_updated_dialogues` or `DialogueCsvError` feature; there must be no import error.

- [ ] **Step 3: Implement validated CSV reading and writing**

Add these imports, types, and functions to `scripts/extract_updated_dialogues.py`:

```python
import csv
from dataclasses import dataclass
from pathlib import Path


class DialogueCsvError(ValueError):
    """表示输入 CSV 不符合对话文件格式。"""


@dataclass(frozen=True)
class ExtractionStats:
    old_rows: int
    new_rows: int
    unmatched_occurrences: int
    unique_rows: int


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
```

- [ ] **Step 4: Run the tests and verify GREEN**

Run the unittest discovery command. Expected: seven tests pass with no warnings or errors.

- [ ] **Step 5: Commit CSV safety and output behavior**

```powershell
git add -- scripts/extract_updated_dialogues.py tests/test_extract_updated_dialogues.py
git commit -m "feat(scripts): write validated dialogue update CSV"
```

### Task 3: Steam Build ID workflow and real-data verification

**Files:**
- Modify: `scripts/extract_updated_dialogues.py`
- Modify: `tests/test_extract_updated_dialogues.py`

**Interfaces:**
- Consumes: The maintainer-edited `STEAM_BUILD_ID`, fixed old CSV path, and repository-relative new CSV path.
- Produces: `resources/dialogue_filtered_<STEAM_BUILD_ID>.csv` and a console summary; `main() -> int` returns `0` on success and `1` on validation or file errors.

- [ ] **Step 1: Add failing build-ID and path tests**

Extend imports and add:

```python
def build_output_path(*args):
    return require_feature("build_output_path")(*args)


class BuildOutputPathTests(unittest.TestCase):
    def test_builds_repository_resource_path_for_valid_build_id(self):
        project_root = Path("D:/project")

        output = build_output_path(project_root, "19283746")

        self.assertEqual(
            project_root / "resources" / "dialogue_filtered_19283746.csv",
            output,
        )

    def test_rejects_empty_build_id(self):
        with self.assertRaisesRegex(ValueError, "STEAM_BUILD_ID 不能为空"):
            build_output_path(Path("D:/project"), "")

    def test_rejects_filename_unsafe_build_id(self):
        with self.assertRaisesRegex(ValueError, "只能包含"):
            build_output_path(Path("D:/project"), "123/456")
```

- [ ] **Step 2: Run the tests and verify RED**

Run the unittest discovery command. Expected: the seven existing tests pass and the three new tests fail with assertions containing `缺少待实现功能: build_output_path`; there must be no import error.

- [ ] **Step 3: Add constants, build-ID validation, and the command entry point**

Add `re` and `sys` imports and complete `scripts/extract_updated_dialogues.py` with:

```python
import re
import sys

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent

STEAM_BUILD_ID = ""  # 在这里填写 Steam Build ID
OLD_DIALOGUE_FILTERED_CSV = Path(
    r"D:\SteamLibrary\steamapps\common\Rhell\BepInEx\plugins\resources\dialogue_filtered.csv"
)
NEW_DIALOGUE_CSV = PROJECT_ROOT / "resources" / "dialogue.csv"
SAFE_BUILD_ID_PATTERN = re.compile(r"^[A-Za-z0-9._-]+$")


def build_output_path(project_root, build_id):
    if not build_id:
        raise ValueError("STEAM_BUILD_ID 不能为空，请填写 Steam Build ID")
    if not SAFE_BUILD_ID_PATTERN.fullmatch(build_id):
        raise ValueError("STEAM_BUILD_ID 只能包含字母、数字、点、下划线和连字符")
    return Path(project_root) / "resources" / f"dialogue_filtered_{build_id}.csv"


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
```

- [ ] **Step 4: Run unit tests and verify GREEN**

Run the unittest discovery command. Expected: ten tests pass with no warnings or errors.

- [ ] **Step 5: Verify the current real files without writing into `resources/`**

Run the public extraction function against the real inputs and a temporary output directory:

```powershell
@'
import csv
import tempfile
from pathlib import Path

from scripts.extract_updated_dialogues import extract_updated_dialogues

old_path = Path(r"D:\SteamLibrary\steamapps\common\Rhell\BepInEx\plugins\resources\dialogue_filtered.csv")
new_path = Path(r"D:\projects\RhellHan\resources\dialogue.csv")

with tempfile.TemporaryDirectory() as temp_dir:
    output_path = Path(temp_dir) / "dialogue_filtered_verification.csv"
    stats = extract_updated_dialogues(old_path, new_path, output_path)
    with output_path.open(encoding="utf-8-sig", newline="") as csv_file:
        rows = list(csv.reader(csv_file))
    assert stats.old_rows == 2261, stats
    assert stats.new_rows == 6385, stats
    assert stats.unmatched_occurrences == 50, stats
    assert stats.unique_rows == 11, stats
    assert len(rows) == 11, len(rows)
    assert all(len(row) == 3 and row[2] == "" for row in rows)
    print(stats)
'@ | py -
```

Expected: `ExtractionStats(old_rows=2261, new_rows=6385, unmatched_occurrences=50, unique_rows=11)` and exit code 0.

- [ ] **Step 6: Run repository hygiene checks**

```powershell
py -m py_compile scripts/extract_updated_dialogues.py tests/test_extract_updated_dialogues.py
git diff --check
git status --short
```

Expected: compilation and whitespace checks exit 0; status shows only the intended implementation/test changes plus the two pre-existing user-modified scripts.

- [ ] **Step 7: Commit the completed workflow**

```powershell
git add -- scripts/extract_updated_dialogues.py tests/test_extract_updated_dialogues.py
git commit -m "feat(scripts): add Steam build dialogue update extractor"
```
