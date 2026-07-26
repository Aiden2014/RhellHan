# Chinese Text Layout Fix Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove generated hard line breaks from item and rune descriptions and let TMP size Chinese dialogue from the real text rectangle instead of the game's character-count cap.

**Architecture:** Add one Unity-independent `TextLayoutPolicy` that preserves semantic description text and selects the dialogue maximum font size. `TranslationManager` and the existing `DialogueUI.SetDialogueSection` postfix consume this policy, while a dependency-free console regression harness compiles the same policy source and verifies it without loading Unity.

**Tech Stack:** C# 12, .NET Standard 2.1 plugin, .NET 8 console regression harness, BepInEx, Harmony, Unity TextMeshPro.

## Global Constraints

- Preserve newlines explicitly authored in CSV translations.
- Do not change non-Chinese dialogue layout.
- Preserve a nonzero `DialogueSegment.FontSize` chosen by the game content.
- Let TMP reduce the actual font size when rendered width or height requires it.
- Limit this change to item/rune descriptions and the shared dialogue box; leave the other `InsertManualBreaks` call sites unchanged.
- Preserve the user's existing unstaged changes in `.editorconfig` and the texture-replacement section of `Plugin.cs`.

## File Structure

- Create `TextLayoutPolicy.cs`: pure, Unity-independent description and dialogue sizing policy.
- Create `tests/RhellHan.LayoutTests/RhellHan.LayoutTests.csproj`: dependency-free executable regression project.
- Create `tests/RhellHan.LayoutTests/Program.cs`: assertions for hard-break preservation and font-size selection.
- Modify `RhellHan.csproj`: exclude test source files from the plugin's default recursive compile glob.
- Modify `TranslationManager.cs`: route item/rune description values through the semantic-text policy instead of `InsertManualBreaks`.
- Modify `Plugin.cs`: apply the Chinese automatic-size policy after the original `SetDialogueSection` method.

---

### Task 1: Add the text-layout regression harness and implement the policy

**Files:**
- Create: `tests/RhellHan.LayoutTests/RhellHan.LayoutTests.csproj`
- Create: `tests/RhellHan.LayoutTests/Program.cs`
- Create: `TextLayoutPolicy.cs`
- Modify: `RhellHan.csproj`
- Modify: `TranslationManager.cs:363-383`
- Modify: `Plugin.cs:532-562`

**Interfaces:**
- Produces: `TextLayoutPolicy.PrepareDescription(string translatedText) -> string`
- Produces: `TextLayoutPolicy.GetDialogueFontSizeMax(string text, float authoredFontSize, float gameFontSizeMax) -> float`
- Consumes: `DialogueSegment.dialogue`, `DialogueSegment.FontSize`, and the original `TMP_Text.fontSizeMax` value.

- [x] **Step 1: Add the dependency-free test project without production policy code**

Add this exclusion to the main `RhellHan.csproj` so the plugin does not compile the console test source:

```xml
  <ItemGroup>
    <Compile Remove="tests/**/*.cs" />
  </ItemGroup>
```

Create `tests/RhellHan.LayoutTests/RhellHan.LayoutTests.csproj`:

```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net8.0</TargetFramework>
    <ImplicitUsings>enable</ImplicitUsings>
    <Nullable>disable</Nullable>
  </PropertyGroup>
</Project>
```

Create `tests/RhellHan.LayoutTests/Program.cs`:

```csharp
namespace RhellHan;

internal static class Program
{
    private static int _failures;

    private static int Main()
    {
        Run("long Chinese descriptions do not gain generated newlines", () =>
        {
            const string text =
                "那个于你瞳孔深处颤动的黑色核心正透过模糊的视野凝视前方它被封装在宇宙那沉睡的汪洋中令那关于理解之顶点的提示如日落般隐没与此同时闪烁的大脑升腾入天际与创造之五手再度合而为一而那些本不该仰望星空之人的诅咒就在那里";
            Equal(text, TextLayoutPolicy.PrepareDescription(text));
            False(TextLayoutPolicy.PrepareDescription(text).Contains('\n'));
        });

        Run("authored newlines are preserved", () =>
        {
            const string text = "第一行\n第二行";
            Equal(text, TextLayoutPolicy.PrepareDescription(text));
        });

        Run("automatic Chinese dialogue can use the normal maximum", () =>
        {
            Equal(
                80f,
                TextLayoutPolicy.GetDialogueFontSizeMax("一幅画着大圆圈的符文图纸。", 0f, 55f)
            );
        });

        Run("explicit Chinese font size keeps the game maximum", () =>
        {
            Equal(42f, TextLayoutPolicy.GetDialogueFontSizeMax("中文", 42f, 42f));
        });

        Run("English dialogue keeps the game maximum", () =>
        {
            Equal(55f, TextLayoutPolicy.GetDialogueFontSizeMax("English dialogue", 0f, 55f));
        });

        Run("Chinese inside rich text uses the normal maximum", () =>
        {
            Equal(
                80f,
                TextLayoutPolicy.GetDialogueFontSizeMax(
                    "<color=#C7850F>抵消</color>魔法",
                    0f,
                    55f
                )
            );
        });

        return _failures;
    }

    private static void Run(string name, Action test)
    {
        try
        {
            test();
            Console.WriteLine($"PASS: {name}");
        }
        catch (Exception error)
        {
            _failures++;
            Console.Error.WriteLine($"FAIL: {name}: {error.Message}");
        }
    }

    private static void Equal<T>(T expected, T actual)
    {
        if (!EqualityComparer<T>.Default.Equals(expected, actual))
            throw new InvalidOperationException($"expected '{expected}', got '{actual}'");
    }

    private static void False(bool value)
    {
        if (value)
            throw new InvalidOperationException("expected false, got true");
    }
}
```

- [x] **Step 2: Run the regression harness and verify RED**

Run:

```powershell
dotnet run --project tests\RhellHan.LayoutTests\RhellHan.LayoutTests.csproj
```

Expected: compilation fails with `CS0103` because `TextLayoutPolicy` does not exist. This is the intended RED failure; restore or package errors are not acceptable substitutes.

- [x] **Step 3: Add the pure production policy to the test project**

Add this item group to `tests/RhellHan.LayoutTests/RhellHan.LayoutTests.csproj`:

```xml
  <ItemGroup>
    <Compile Include="..\..\TextLayoutPolicy.cs" Link="TextLayoutPolicy.cs" />
  </ItemGroup>
```

Create `TextLayoutPolicy.cs`:

```csharp
namespace RhellHan;

internal static class TextLayoutPolicy
{
    internal const float AutomaticChineseDialogueFontSizeMax = 80f;

    internal static string PrepareDescription(string translatedText)
    {
        return translatedText;
    }

    internal static float GetDialogueFontSizeMax(
        string text,
        float authoredFontSize,
        float gameFontSizeMax
    )
    {
        if (authoredFontSize == 0f && ContainsChinese(text))
            return AutomaticChineseDialogueFontSizeMax;

        return gameFontSizeMax;
    }

    private static bool ContainsChinese(string text)
    {
        if (string.IsNullOrEmpty(text))
            return false;

        for (int i = 0; i < text.Length; i++)
        {
            if (text[i] >= 0x4E00 && text[i] <= 0x9FFF)
                return true;
        }

        return false;
    }
}
```

- [x] **Step 4: Wire semantic description loading and the dialogue postfix**

In `TranslationManager.LoadAndSortDescription`, replace the generated-break call:

```csharp
var value = TextLayoutPolicy.PrepareDescription(row.TranslationTranslatedText);
translationList.Add(value);
```

In `Hooks.DialogueUI_SetDialogueSection_Postfix`, resolve `currentDialogue` before the fixer early return, validate `dex`, and apply the policy after the original method has selected its character-count maximum:

```csharp
var currentDialogue = Traverse
    .Create(__instance)
    .Field("currentDialogue")
    .GetValue<List<DialogueSegment>>();

if (currentDialogue != null && dex >= 0 && dex < currentDialogue.Count)
{
    var segment = currentDialogue[dex];
    __instance.dialogueBox.fontSizeMax = TextLayoutPolicy.GetDialogueFontSizeMax(
        segment.dialogue,
        segment.FontSize,
        __instance.dialogueBox.fontSizeMax
    );
}
```

Keep the existing fixer state update below this block. Do not duplicate the traversal or return before applying the layout policy.

- [x] **Step 5: Run the regression harness and verify GREEN**

Run:

```powershell
dotnet run --project tests\RhellHan.LayoutTests\RhellHan.LayoutTests.csproj
```

Expected: six `PASS:` lines and exit code 0.

- [x] **Step 6: Format only the files owned by this change**

Run:

```powershell
csharpier format TextLayoutPolicy.cs TranslationManager.cs tests\RhellHan.LayoutTests\Program.cs
```

Do not format all of `Plugin.cs`, because it contains pre-existing user changes. Keep the `Plugin.cs` edit manually consistent with the surrounding C# style.

- [x] **Step 7: Re-run tests after formatting**

Run:

```powershell
dotnet run --project tests\RhellHan.LayoutTests\RhellHan.LayoutTests.csproj
```

Expected: six `PASS:` lines and exit code 0.

- [x] **Step 8: Build the plugin against the configured game assemblies**

Run:

```powershell
dotnet build --no-restore
```

Expected: build succeeds with 0 errors. Record any existing analyzer warnings separately; do not weaken analyzer configuration as part of this fix.

- [x] **Step 9: Inspect the final diff for scope and user-change preservation**

Run:

```powershell
git -c safe.directory=D:/projects/RhellHan diff --check
git -c safe.directory=D:/projects/RhellHan diff -- TextLayoutPolicy.cs TranslationManager.cs Plugin.cs RhellHan.csproj tests/RhellHan.LayoutTests
```

Expected: no whitespace errors; `Plugin.cs` contains the user's existing texture-replacement changes plus only the targeted dialogue postfix edit; `.editorconfig` is untouched by this task.

- [x] **Step 10: Commit only the layout-fix files**

Stage only the new helper, tests, project file, and the precise owned hunks from `TranslationManager.cs` and `Plugin.cs`. Because `Plugin.cs` already contains user changes, do not use an unrestricted `git add Plugin.cs`; stage the layout hunk selectively and confirm it with `git diff --cached`.

Commit message:

```text
fix(dialogue): let TMP lay out Chinese descriptions
```

- [ ] **Step 11: Hand off manual game verification**

Provide the built DLL path `bin/Debug/netstandard2.1/RhellHan.dll` and ask the user to replay Tender Noodles, Rainbow Gummi, Area/Rise, Void, a portrait dialogue, and an English dialogue. If any case still shrinks unexpectedly, collect one targeted TMP layout snapshot containing rectangle size, actual/min/max font size, line count, and per-line width before changing another layout variable.
