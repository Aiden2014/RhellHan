# Chinese Text Layout Fix Design

## Problem

Chinese item and rune descriptions are laid out twice before they reach the screen:

1. `TranslationManager.InsertManualBreaks` inserts a hard newline after a fixed
   logical width. With `maxWidth = 50` and every non-ASCII character counted as
   two units, this means one hard newline every 25 Chinese characters.
2. `DialogueUI.SetDialogueSection` chooses `TMP_Text.fontSizeMax` from the text's
   character count. Without portraits, the maximum changes abruptly from 80 to
   55 when the count rises from 35 to 36. The thresholds are reduced further when
   character portraits narrow the text rectangle.

The hard newlines ignore the actual `RectTransform`, font metrics, resolution,
and portrait layout. TMP may then wrap a hard-broken line again. The inserted
newline also contributes to the game's length heuristic, which can lower the
maximum font size even when the rendered text would fit.

## Evidence

- All thirteen reported screenshots map to translations in
  `item_description.csv` or `rune_description.csv`.
- Re-running `InsertManualBreaks(text, 50)` reproduces the exact forced line
  endings in the screenshots, including the five lines of the Void rune.
- Inspection of `Assembly-CSharp.dll` shows that `DialogueUI.SetDialogueSection`
  sets `fontSizeMax` from the visible character count instead of rendered text
  dimensions. A 35-character translation receives a maximum of 80, while a
  36-character translation receives 55 when no portraits are present.

## Approaches Considered

### 1. Increase the fixed manual width

Changing 50 to a larger constant would move the symptoms but would still be
wrong at other resolutions, with portraits, and in differently sized UI panels.
It is not selected.

### 2. Make the manual breaker CJK-aware

Measuring Chinese glyphs more accurately would improve one layout, but the data
loading layer still does not know the final text rectangle or TMP settings. It
would also duplicate TMP's layout engine. It is not selected.

### 3. Keep translations semantic and let TMP lay them out

Store item and rune descriptions without generated newlines. After the original
`SetDialogueSection` finishes configuring the active section, remove the
character-count maximum for Chinese text and let TMP autosizing and wrapping use
the actual rectangle and fallback font metrics. This is the selected approach.

## Design

### Translation loading

`LoadAndSortDescription` will store `TranslationTranslatedText` unchanged. Only
newlines explicitly present in the CSV remain. This fixes both item and rune
descriptions because they share the same loader.

The other `InsertManualBreaks` call sites are outside this first change. They use
different controls and rectangle sizes, so they will be handled separately after
the dialogue fix is verified in game.

### Dialogue layout override

The existing `DialogueUI.SetDialogueSection` postfix will retain the bold and
wobble state work. For a section containing Chinese text and using the game's
automatic font-size choice, it will raise `dialogueBox.fontSizeMax` to the normal
dialogue maximum of 80. TMP remains responsible for choosing a smaller actual
font size when the real width or height requires it.

Sections with an explicit nonzero `DialogueSegment.FontSize` keep the author's
requested maximum. Non-Chinese dialogue is not changed.

The override runs after the original method so it replaces only the faulty
length heuristic without duplicating portrait-offset or textbox setup.

### Testable policy

Small pure helpers will express the two decisions:

- description translations do not gain generated line breaks;
- automatic Chinese dialogue uses the normal maximum, while explicit-size and
  non-Chinese sections retain the game's result.

This keeps regression tests independent of Unity scene loading.

## Verification

Automated verification will cover:

- a 25+ character Chinese description remains a single semantic string;
- existing intentional newlines are preserved;
- Chinese automatic-size dialogue selects maximum 80;
- explicit-size Chinese and English dialogue keep the current maximum;
- the plugin builds against the configured game assemblies.

Manual game verification should replay representative cases from the report:

- Tender Noodles and Wriggling Pearl for premature wrapping;
- Rainbow Gummi and Area/Rise runes for unnecessary shrinking;
- Void rune for long-text use of the full horizontal area;
- one dialogue with one or two character portraits;
- one English dialogue to confirm unchanged behavior.

The success criterion is that no generated newline fixes a line ending in place,
and font size decreases only when the rendered text cannot fit the active text
rectangle.
