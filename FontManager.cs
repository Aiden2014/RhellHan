using System.Collections.Generic;
using TMPro;

namespace RhellHan;

public static class FontManager
{
    public static bool HasFallback(TMP_FontAsset font, string fallbackName)
    {
        if (font?.fallbackFontAssetTable == null)
            return false;

        for (int i = 0; i < font.fallbackFontAssetTable.Count; i++)
        {
            var existing = font.fallbackFontAssetTable[i];
            if (existing != null && existing.name == fallbackName)
            {
                return true;
            }
        }

        return false;
    }

    public static void SaveFallbackFont(TMP_FontAsset __instance, TMP_FontAsset chineseFallbackFont)
    {
        __instance.fallbackFontAssetTable ??= [];

        bool alreadyAdded = false;
        for (int i = 0; i < __instance.fallbackFontAssetTable.Count; i++)
        {
            if (__instance.fallbackFontAssetTable[i].name == chineseFallbackFont.name)
            {
                alreadyAdded = true;
                break;
            }
        }

        if (!alreadyAdded)
        {
            __instance.fallbackFontAssetTable.Add(chineseFallbackFont);
        }
    }
}
