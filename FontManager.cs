using TMPro;
using UnityEngine;

namespace RhellHan;

public static class FontManager
{
    public const float ChineseNormalFaceDilate = 0f;
    public const float ChineseBoldFaceDilate = 0.35f;
    public const float ChineseBoldSpacing = 8f;

    private static bool _chineseFontConfigured;

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
        if (chineseFallbackFont == null)
            return;

        __instance.fallbackFontAssetTable ??= new System.Collections.Generic.List<TMP_FontAsset>();

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

        if (!_chineseFontConfigured)
        {
            _chineseFontConfigured = true;
            chineseFallbackFont.normalStyle = ChineseNormalFaceDilate;
            chineseFallbackFont.boldStyle = ChineseBoldFaceDilate;
            chineseFallbackFont.boldSpacing = ChineseBoldSpacing;
            if (
                chineseFallbackFont?.material != null
                && chineseFallbackFont.material.HasProperty(ShaderUtilities.ID_FaceDilate)
            )
            {
                chineseFallbackFont.material.SetFloat(
                    ShaderUtilities.ID_FaceDilate,
                    ChineseNormalFaceDilate
                );
                Plugin.Logger.LogInfo(
                    $"Configured Chinese font '{chineseFallbackFont.name}' "
                        + $"normalStyle={ChineseNormalFaceDilate}, "
                        + $"boldStyle={ChineseBoldFaceDilate}"
                );
            }
        }
    }
}
