# RhellHan

> [中文文档](README_zh.md)

Complete Chinese localization mod for *Rhell*, using runtime TextMeshPro interception, fallback font injection, and per-frame glyph rendering fixes to work around the game's lack of built-in CJK support.

## Overview

RhellHan provides full Simplified Chinese localization for *Rhell*. The game uses Unity's TextMeshPro for all in-game text, which does not ship with CJK character coverage. To add Chinese support without modifying original game assets, this mod injects a Chinese TMP_FontAsset as a fallback on every loaded font, and applies Harmony runtime patches across all major text-displaying game systems.

Core components:

1. **Runtime Translation** — BepInEx + Harmony plugin that intercepts dialogue, UI text, inventory, map hints, story points, dialogue choices, cheat menus, challenge menus, world/area names, and spell selection, then substitutes English strings with Chinese translations from CSV dictionaries.
2. **Fallback Font Injection** — Hooks `TMP_FontAsset.ReadFontAssetDefinition` to register a Chinese TMP font as a fallback on every font asset the game loads.
3. **UI Font Replacement** — For legacy `UnityEngine.UI.Text` components, replaces the font entirely with a Chinese variant loaded from the same AssetBundle.
4. **Glyph Thickness Fixer** — A `MonoBehaviour` attached to dialogue boxes post-translation that adjusts `FaceDilate` on `TMP_SubMeshUI` materials every frame, fixing rendering artifacts on dynamically-generated fallback glyphs.
5. **TextMeshPro Text Translation** — Patches `TextMeshPro.Awake` and `UIBehaviour.Start` to translate TextMeshPro UGUI text at startup.
6. **Cheat Menu Translation** — Translates cheat rune titles and descriptions in `CheatRuneBook.SetupCheatMenu`.
7. **Challenge Menu Translation** — Translates challenge names in `ChallengeMenu.SetupValues`.
8. **Selectable Spell Translation** — Translates spell names and descriptions in `UISelectableSpell.GetTitle`.
9. **World/Area Name Translation** — Patches `MainMenuUi.Start` and `MapHandle.SelectLocation` to replace world area names.
10. **Sort Text Localization** — Replaces the sort type labels in `UiItemsHandle` with Chinese equivalents.

## Interesting Techniques

- **Fallback Font Strategy**: Rather than modifying the game's existing TMP fonts, the plugin hooks into `TMP_FontAsset.ReadFontAssetDefinition` and appends a pre-built Chinese SDF font as a fallback. TextMeshPro automatically uses the fallback for any character missing from the primary font — no per-font-asset modification needed.
- **TMP SubMesh Glyph Fixing**: When TextMeshPro renders fallback glyphs, it creates `TMP_SubMeshUI` objects whose materials can have incorrect `FaceDilate` values, causing visual artifacts. The `FallbackFontThicknessFixer` runs every frame adjusting this shader property on all sub-meshes in dialogue boxes.
- **CSV Key Batching with `|||`**: Multi-segment text (dialogues, summaries, dialogue options) is joined with `|||` as a delimiter to form compound lookup keys, preserving the segment structure through translation.
- **Dialogue Choice Width Adjustment**: After translating dialogue options, the plugin measures the preferred width of each option using `TMP_Text.GetPreferredValues()` and dynamically resizes the choice buttons, with a wider cap for CJK text (550px vs 485px for English).

## Technologies & Libraries

- **[BepInEx 5.x](https://github.com/BepInEx/BepInEx)** — Unity game modding framework providing plugin loading and logging.
- **[HarmonyLib 2.x](https://github.com/pardeike/Harmony)** — Runtime method patching library for non-invasive code injection.
- **[Unity Editor 2020.3.49f1c1](https://unity.com/)** — Used with TextMeshPro's Font Asset Creator to generate the Chinese TMP_FontAsset from `KNMaiyuan-Regular` and package it into an AssetBundle.
- **[UABEANext](https://github.com/nesrak1/UABEANext)** — Unity Asset Bundle Extractor, used to extract MonoBehaviour text data from the game's asset bundles for building translation source CSVs.
- **[DnSpy-MCPserver-Extension](https://github.com/AgentSmithers/DnSpy-MCPserver-Extension)** — dnSpyEx MCP server enabling programmatic IL inspection and patching. Used during development to explore game assembly methods, identify injection points, and verify Harmony patch targets.
- **[ParaTranz](https://paratranz.cn/)** — Collaborative translation management platform for crowdsourced localization.

## Custom Font Workflow

Since *Rhell* only ships Latin-character TMP fonts, we need to generate a Chinese fallback:

1. **Extract required characters** — Run `scripts/extract_unique_non_ascii_chars.py` to collect all unique non-ASCII characters from the translated CSV files. By default it writes `resources/unique_non_ascii_chars.txt`.
2. **Create the TMP font asset** — In Unity Editor 2020.3.49f1c1, import the `KNMaiyuan-Regular` font and the generated `unique_non_ascii_chars.txt`, then open TextMeshPro's Font Asset Creator.
3. **Use the font creator settings** — Set the source font to `KNMaiyuan-Regular`, Sampling Point Size to `Auto Sizing`, Padding to `5`, Packing Method to `Fast`, Atlas Resolution to `2048 x 2048`, Character Set to `Characters from File`, Character File to `unique_non_ascii_chars`, Render Mode to `SDFAA`, and enable `Get Kerning Pairs`. Generate and save the TMP font asset as `KNMaiyuan-Regular SDF`.
4. **Package into AssetBundle** — Use Unity's Asset Bundle tooling to package the TMP font asset and the `KNMaiyuan-Regular` font into `chinese_font.bundle`.
5. **Install the bundle** — Place `chinese_font.bundle` in `Rhell\BepInEx\plugins\resources` (or the equivalent `BepInEx/plugins/resources/` folder for your game install). The plugin loads it via `AssetBundle.LoadFromFile()`.

## Project Structure

```text
RhellHan/
├── resources/                           # Translation data and font bundles
│   ├── challenge_menu.csv               # Challenge menu translations
│   ├── cheat_description.csv            # Cheat rune description translations
│   ├── cheat_title.csv                  # Cheat rune title translations
│   ├── dialogue.csv                     # Raw dialogue extractions (unfiltered)
│   ├── dialogue_filtered.csv            # Dialogue translations (|||-batched keys)
│   ├── dialogue_option.csv              # Dialogue choice translations
│   ├── endpoint.csv                     # Endpoint text translations
│   ├── hint.csv                         # Pause menu hint translations
│   ├── item_description.csv             # Item description translations
│   ├── item_name.csv                    # Item name translations
│   ├── item_tab_description.csv         # Inventory tab description translations
│   ├── json_diff.txt                    # JSON comparison output for translation QA
│   ├── map_location_hightlight.csv      # Map location highlight translations
│   ├── room_hint.csv                    # Room hint translations
│   ├── rune_description.csv             # Rune description translations
│   ├── rune_name.csv                    # Rune name translations
│   ├── selectable_spell_description.csv # Spell description translations
│   ├── selectable_spell_name.csv        # Spell name translations
│   ├── storypoint.csv                   # Story point text translations
│   ├── storypoint_mapping.csv           # Story point ID-to-text mapping
│   ├── storypoint_missing.csv           # Missing/untranslated story points
│   ├── summary.csv                      # End-of-run summary translations
│   ├── summarypoint.csv                 # Summary point text translations
│   ├── text.csv                         # Legacy UI text translations
│   ├── text_mesh_pro.csv                # TextMeshPro text translations
│   ├── text_mesh_pro_ugui.csv           # TextMeshPro UGUI text translations
│   ├── world_name.csv                   # World/area name translations
│   └── unique_non_ascii_chars.txt       # Extracted character list for font generation
├── scripts/                             # Python automation tools
│   ├── compare_hints_arrays.py          # Diff hint arrays across versions
│   ├── compare_json_files.py            # Diff JSON exports for translation QA
│   ├── extract_and_merge_texts_v2.py    # Extract and merge text assets
│   ├── extract_challenge_menu_to_csv.py # Extract challenge menu text
│   ├── extract_cheat_to_csv.py          # Extract cheat menu titles and descriptions
│   ├── extract_dialogues_from_monobehaviour.py
│   ├── extract_dialogues_options_from_monobehaviour.py
│   ├── extract_endpoint_summarypoint.py # Extract endpoint and summary point text
│   ├── extract_hints_from_monobehaviour.py
│   ├── extract_inventory_to_csv.py      # Extract rune/item names and descriptions
│   ├── extract_map_location_highlights.py
│   ├── extract_room_hints.py
│   ├── extract_storypoints_from_monobehaviour.py
│   ├── extract_summaries_from_monobehaviour.py
│   ├── extract_text_mesh_pro.py         # Extract TextMeshPro text from assets
│   ├── extract_text_mesh_pro_ugui.py    # Extract TextMeshPro UGUI text
│   ├── extract_texts_from_monobehaviour.py
│   ├── extract_ui_item_tab_descriptions.py
│   ├── extract_ui_selectable_spell_level3_to_csv.py
│   ├── extract_unique_non_ascii_chars.py # Collect non-ASCII chars for font generation
│   ├── extract_world_names.py
│   └── filter_and_deduplicate_dialogues.py
├── FontManager.cs                       # Fallback font registration on TMP_FontAsset load
├── Plugin.cs                            # BepInEx entry point and all Harmony patches
├── ResourceLoader.cs                    # AssetBundle loading and CSV parsing
├── TranslationManager.cs                # CSV dictionary initialization and lookup
├── RhellHan.csproj                      # .NET Standard 2.1 build configuration
└── RhellHan.sln                         # Solution file
```

## License

### Project Code

Released under the **[GNU LGPL v2.1](LICENSE)** license.

### Third-Party Components

- **BepInEx**: [LGPL-2.1](https://github.com/BepInEx/BepInEx/blob/master/LICENSE)
- **HarmonyLib**: [MIT](https://github.com/pardeike/Harmony/blob/master/LICENSE)

### Translation Content

Translation content is from the [ParaTranz Platform](https://paratranz.cn/projects/18570), licensed under **CC BY-NC 4.0**.

---

**Note**: This project is for educational purposes only. Please support the original game.
