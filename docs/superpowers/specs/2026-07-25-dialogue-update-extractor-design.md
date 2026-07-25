# Dialogue Update Extractor Design

## Goal

Add a Python script under `scripts/` that compares the previously translated
`dialogue_filtered.csv` with the newly extracted `resources/dialogue.csv` and
writes only new or changed English dialogue lines to a Steam-build-specific CSV.

## Inputs and configuration

The script exposes three constants near the top of the file:

- `STEAM_BUILD_ID = ""`, intentionally left empty for the maintainer to fill in.
- `OLD_DIALOGUE_FILTERED_CSV`, defaulting to
  `D:\SteamLibrary\steamapps\common\Rhell\BepInEx\plugins\resources\dialogue_filtered.csv`.
- The new CSV path, resolved from the repository rather than the current working
  directory, as `resources/dialogue.csv`.

The output path is also repository-relative:
`resources/dialogue_filtered_<STEAM_BUILD_ID>.csv`.

## Matching and deduplication

CSV files are read with Python's standard `csv` module and `utf-8-sig`
encoding. The second column is the English dialogue text.

The script builds a set of all English texts in the old translated file. It
then scans the new raw file in source order. A new row is selected when its
English text does not exactly match any old English text. Exact matching is
intentional: case, punctuation, Unicode punctuation, and leading or trailing
spaces can all represent a game update that needs review.

Selected rows are deduplicated by their exact English text. If the same changed
text occurs in multiple dialogue arrays, only its first occurrence in the new
CSV is retained. This minimizes translation work while preserving a valid
new-version locator in the first column. With the files inspected on 2026-07-25,
this rule selects 11 unique texts from 50 raw occurrences.

## Output format

Each output row contains exactly three columns:

1. The first-column locator copied from the selected new row.
2. The updated English dialogue copied from the selected new row.
3. An empty translation field.

The file is written with `utf-8-sig`, `newline=""`, and Python's standard CSV
quoting behavior. No header is added, matching the existing dialogue files.
The script prints input counts, the number of raw unmatched occurrences, the
number of unique rows written, and the output path.

## Validation and errors

The script exits with a clear non-zero error before writing output when:

- `STEAM_BUILD_ID` is empty or contains characters unsafe for a filename.
- Either input file does not exist or is not a regular file.
- A CSV row has fewer than two columns.

Validation happens before opening the output file, so invalid input cannot
truncate an existing update CSV. A successful run may replace the output file
for the configured build ID, making repeated runs deterministic.

## Alternatives considered

Matching by array identifier and index was rejected because game updates change
array identifiers; the inspected files would produce roughly 4,502 false
positives. Comparing complete dialogue arrays was also rejected because a
single corrected line would pull unchanged neighboring dialogue into the update
file. Exact English-text set difference directly represents the requested
translation workload.

## Testing

Standard-library `unittest` tests will use temporary CSV files and exercise the
public comparison function without touching production resources. Tests cover:

- Selecting new and spelling-corrected English text.
- Excluding text already present in the old translated file.
- Deduplicating repeated changed text while preserving its first new row.
- Preserving exact whitespace and punctuation distinctions.
- Rejecting malformed rows before writing output.
- Rejecting an empty or filename-unsafe Steam Build ID.

After unit tests pass, the script will be run against the current real inputs
with a temporary test build ID. The generated CSV will be inspected for an
11-row result and then removed without changing either input file.
