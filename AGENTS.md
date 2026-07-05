# AGENTS.md

This file provides guidance to Codex (Codex.ai/code) when working with code in this repository.

## Project Overview

RhellHan is a **BepInEx plugin** that adds Chinese localization to the Unity game **Rhell**. It patches game systems at runtime via Harmony to replace English text with Chinese translations loaded from CSV files, and injects a Chinese fallback font via AssetBundles.

## Build & Development

```bash
# Build (GamePath defaults to D:\SteamLibrary\steamapps\common\Rhell)
dotnet build

# Build with a custom game path
dotnet build -p:GamePath="C:\path\to\Rhell"

# The built DLL goes to bin/Debug/netstandard2.1/RhellHan.dll
# Copy it to the game's BepInEx/plugins directory for testing
```

There are no tests in this project.

## Architecture

### Core classes

- **`Plugin.cs`** — BepInEx entry point (`BaseUnityPlugin`). `Awake()` initialises `TranslationManager`, binds config, and applies all Harmony patches via `Hooks`. The `Hooks` static class contains every Harmony patch across the game's systems (dialogue, UI text, inventory, map, story points, dialogue choices). Each patch intercepts a game method, looks up translations in `TranslationManager`, and mutates the relevant fields.

- **`TranslationManager.cs`** — Singleton initialiser that loads 15 translation categories from CSV into dictionaries/lists. Each `Init*` method reads a specific CSV (e.g. `dialogue_filtered.csv`, `text.csv`, `text_mesh_pro.csv`, `cheat_title.csv`, `challenge_menu.csv`) and builds lookups keyed on the original English text (joined with `|||` for multi-segment entries).

- **`ResourceLoader.cs`** — Two responsibilities: (1) loads Unity AssetBundles from `BepInEx/plugins/resources/` for Chinese TMP fonts and UI fonts, with caching; (2) parses CSV files with a custom parser that handles quoted commas and `|||` multi-key delimiters, yielding `TranslationRow` objects.

- **`FontManager.cs`** — Registers a Chinese `TMP_FontAsset` as a fallback on any `TMP_FontAsset` that gets loaded (hooked via `TMP_FontAsset.ReadFontAssetDefinition`).

- **`FallbackFontThicknessFixer`** — A Unity `MonoBehaviour` attached to dialogue boxes after translation. Runs every frame adjusting `TMP_SubMeshUI` materials' `FaceDilate` shader property to fix rendering artifacts on dynamically-generated fallback glyphs.

### Translation data flow

1. Python scripts in `scripts/` extract English text from the game's Unity assets/MonoBehaviours into CSV files
2. CSVs are manually translated to Chinese (third column)
3. `TranslationManager.Init()` parses CSVs from `resources/` at plugin startup
4. Harmony patches in `Hooks` look up and substitute translated strings at runtime

### CSV key format

Translation lookups use `|||` as a delimiter to join multi-segment keys:
- **Dialogues**: key = joined original English segments; value = joined Chinese segments
- **Summaries**: same pattern
- **Text** (`text.csv`, `text_mesh_pro.csv`, `text_mesh_pro_ugui.csv`): simple string→string dictionary (1 key, 1 value)
- **Index-based** (runes, items, hints, world names): sorted by numeric index from CSV, stored as ordered `List<string>`
- **Cheat/challenge menus** (`cheat_title.csv`, `cheat_description.csv`, `challenge_menu.csv`): simple string→string dictionary
- **Selectable spells** (`selectable_spell_name.csv`, `selectable_spell_description.csv`): string→string dictionary
- **Map locations, room hints, story points, tab descriptions**: string→string dictionary

### Relevant game types (from Assembly-CSharp)

The plugin patches these game types: `DialogueUI`, `PlayerInventory`, `UISelectableSpell`, `UiStoryHandle`, `UiStoryCtrl`, `MapHandle`, `PauseBeesleHints`, `DialogueChoiceHandle`, `CheatRuneBook`, `ChallengeMenu`, `MainMenuUi`, `UiItemsHandle`, `TextMeshPro`, `Text` (Unity), `TMP_FontAsset`, `UIBehaviour`.

### Namespace

Everything is under the single namespace `RhellHan`.
