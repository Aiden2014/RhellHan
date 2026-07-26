# Inventory Menu Description Wrapping Design

## Problem

Item and rune descriptions are shared by two game surfaces:

- `UiItemsHandle.UpdateDescription` copies `InventoryItem.Description` into the
  inventory menu's legacy `UnityEngine.UI.Text` control.
- `PlayerInventory.PickupItem` passes the same `InventoryItem.Description` to
  the dialogue system.

The dialogue box now lays out unmodified Chinese text correctly, but the legacy
menu control does not find line-break opportunities inside continuous Chinese.
Its Best Fit behavior therefore shrinks a long description into one line.
Restoring generated newlines in `PlayerInventory_FillValueFromSaveFile_Postfix`
would fix the menu while reintroducing premature dialogue wrapping.

## Selected Design

Keep the translated `InventoryItem.Description` semantic and unmodified. Add a
Harmony postfix for `UiItemsHandle.UpdateDescription` and generate line breaks
only in the string assigned to `UiItemsHandle.itemDescription`.

The menu formatter will reuse the previous width policy: ASCII characters count
as one unit, non-ASCII characters count as two units, and a line is limited to
50 units (25 full-width Chinese characters). Existing authored newlines and rich
text tags remain intact.

## Boundaries

- `PlayerInventory_FillValueFromSaveFile_Postfix` continues assigning the raw
  translations loaded from `item_description.csv` and `rune_description.csv`.
- `PlayerInventory.PickupItem` therefore continues feeding raw text to the
  dialogue box.
- Only `UiItemsHandle.UpdateDescription` applies the inventory-menu formatter.
- `UiItemsHandle.UpdateTab` remains responsible for translated tab descriptions
  and is not used for selected item/rune descriptions.

## Verification

The layout test harness will verify that:

- a 26-character Chinese menu description wraps after character 25;
- existing authored newlines are preserved;
- the semantic description policy still returns the original unwrapped text;
- English and short Chinese menu descriptions are unchanged.

The plugin must then build successfully against the game's managed assemblies.
