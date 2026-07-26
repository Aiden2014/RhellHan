# Inventory Menu Description Wrapping Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Wrap Chinese item and rune descriptions in the inventory menu without adding generated newlines to the shared description used by dialogue.

**Architecture:** Keep `InventoryItem.Description` unchanged at the translation/data boundary. Put the fixed-width legacy-menu formatting policy in `TextLayoutPolicy`, then invoke it from a postfix on `UiItemsHandle.UpdateDescription` after the game selects an item or rune.

**Tech Stack:** C#, .NET Standard 2.1, BepInEx 5, Harmony, Unity legacy UI Text, dependency-free .NET 8 layout test harness.

## Global Constraints

- Inventory menu lines use the established 50-unit limit: ASCII is one unit and non-ASCII is two units.
- Preserve authored newlines and rich-text tags.
- Do not mutate the description stored in `PlayerInventory.ItemIndex` or `PlayerInventory.RuneIndex`.
- Do not change dialogue layout behavior.
- There are no game integration tests; verify the pure policy and compile the plugin against the installed game assemblies.

---

### Task 1: Inventory Menu Formatting Policy

**Files:**
- Modify: `tests/RhellHan.LayoutTests/Program.cs`
- Modify: `TextLayoutPolicy.cs`
- Modify: `TranslationManager.cs`

**Interfaces:**
- Consumes: `TextLayoutPolicy.PrepareDescription(string translatedText) -> string`
- Produces: `TextLayoutPolicy.PrepareInventoryMenuDescription(string text) -> string`
- Produces: `TextLayoutPolicy.InsertManualBreaks(string text, int maxWidth) -> string`

- [ ] **Step 1: Write failing menu-formatting tests**

Add literal expectations covering the 25-Chinese-character boundary, authored
newlines, and unchanged short/English strings:

```csharp
Equal(
    "甲乙丙丁戊己庚辛壬癸子丑寅卯辰巳午未申酉戌亥天地人\n和",
    TextLayoutPolicy.PrepareInventoryMenuDescription(
        "甲乙丙丁戊己庚辛壬癸子丑寅卯辰巳午未申酉戌亥天地人和"
    )
);
Equal("第一行\n第二行", TextLayoutPolicy.PrepareInventoryMenuDescription("第一行\n第二行"));
Equal("short English", TextLayoutPolicy.PrepareInventoryMenuDescription("short English"));
Equal("简短中文", TextLayoutPolicy.PrepareInventoryMenuDescription("简短中文"));
```

- [ ] **Step 2: Run the tests and verify RED**

Run:

```powershell
dotnet run --project tests/RhellHan.LayoutTests/RhellHan.LayoutTests.csproj
```

Expected: compilation fails because
`TextLayoutPolicy.PrepareInventoryMenuDescription` does not exist.

- [ ] **Step 3: Implement the minimum menu policy**

Add the menu-specific entry point and move the existing manual-break algorithm
from `TranslationManager` into `TextLayoutPolicy`:

```csharp
internal const int InventoryMenuDescriptionWidth = 50;

internal static string PrepareInventoryMenuDescription(string text)
{
    return InsertManualBreaks(text, InventoryMenuDescriptionWidth);
}
```

Keep the current algorithm's treatment of ASCII width, non-ASCII width, authored
newlines, bracket markers, and rich-text tags exactly the same. Update existing
`TranslationManager` callers to use `TextLayoutPolicy.InsertManualBreaks` so
there is one implementation.

- [ ] **Step 4: Run the layout tests and verify GREEN**

Run:

```powershell
dotnet run --project tests/RhellHan.LayoutTests/RhellHan.LayoutTests.csproj
```

Expected: every test prints `PASS` and the process exits 0.

### Task 2: Inventory Menu Display Hook

**Files:**
- Modify: `Plugin.cs`

**Interfaces:**
- Consumes: `TextLayoutPolicy.PrepareInventoryMenuDescription(string text) -> string`
- Produces: Harmony postfix `UiItemsHandle_UpdateDescription_Postfix(UiItemsHandle __instance)`

- [ ] **Step 1: Add the display-only postfix**

Patch the method that the game's `UIItemSolo.OnSelect` invokes:

```csharp
[HarmonyPatch(typeof(UiItemsHandle), nameof(UiItemsHandle.UpdateDescription))]
[HarmonyPostfix]
public static void UiItemsHandle_UpdateDescription_Postfix(UiItemsHandle __instance)
{
    var text = __instance.itemDescription?.text;
    if (string.IsNullOrEmpty(text) || !text.Any(c => isChineseChar(c)))
    {
        return;
    }

    __instance.itemDescription.text =
        TextLayoutPolicy.PrepareInventoryMenuDescription(text);
}
```

- [ ] **Step 2: Verify tests and plugin compilation**

Run:

```powershell
dotnet run --project tests/RhellHan.LayoutTests/RhellHan.LayoutTests.csproj
dotnet build
```

Expected: tests pass; build completes with zero errors and zero warnings.

- [ ] **Step 3: Review the final diff and commit**

Run:

```powershell
git diff --check
git diff -- TextLayoutPolicy.cs TranslationManager.cs Plugin.cs tests/RhellHan.LayoutTests/Program.cs
git status --short
```

Commit the implementation only after the diff shows menu-only formatting and
the verification commands remain green.
